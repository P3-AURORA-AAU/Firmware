# model_ncnn.py
import numpy as np
import ncnn


class NcnnYolo:
    """
    Optimized NCNN wrapper:
    - loads model once
    - sets NCNN opts (threads, vulkan)
    - creates a fresh extractor per inference (thread-safe enough for single-worker usage)
    """

    def __init__(
        self,
        param_path="yolo11n_ncnn_model/model.ncnn.param",
        bin_path="yolo11n_ncnn_model/model.ncnn.bin",
        input_name="in0",
        output_name="out0",
        num_threads=3,
        use_vulkan=True,
    ):
        self.param_path = param_path
        self.bin_path = bin_path
        self.input_name = input_name
        self.output_name = output_name

        self.net = ncnn.Net()

        # ---- Performance options ----
        # Threads: Pi4 has 4 cores. Often best is 4, sometimes 3 depending on load.
        self.net.opt.num_threads = int(num_threads)

        # Vulkan can help if configured + stable on your image.
        # If you enable it but Vulkan isn't available, load may fail — keep default False.
        self.net.opt.use_vulkan_compute = bool(use_vulkan)

        # If your ncnn build supports these, they can help a bit (harmless if absent in your build)
        # (Not all python bindings expose all opts; safe-guard with getattr)
        for k, v in [
            ("use_fp16_packed", True),
            ("use_fp16_storage", True),
            ("use_fp16_arithmetic", True),
        ]:
            if hasattr(self.net.opt, k):
                setattr(self.net.opt, k, v)

        # ---- Load once ----
        self.net.load_param(self.param_path)
        self.net.load_model(self.bin_path)

    def infer(self, in_chw: np.ndarray) -> np.ndarray:
        """
        in_chw: numpy array (C,H,W) float32
        returns: numpy array from out0
        """
        if in_chw.dtype != np.float32:
            in_chw = in_chw.astype(np.float32, copy=False)

        # NCNN Mat expects (w,h,c) when constructed from numpy in many bindings.
        # Your original code passed (3,640,640). Keep same behavior:
        mat_in = ncnn.Mat(in_chw)

        with self.net.create_extractor() as ex:
            # Per-inference extractor settings can help keep CPU usage predictable:
            # (again, not all bindings expose these)
            if hasattr(ex, "set_num_threads"):
                ex.set_num_threads(self.net.opt.num_threads)

            ex.input(self.input_name, mat_in)

            _, out0 = ex.extract(self.output_name)
            return np.array(out0)


# --- Example / quick test ---
def test_inference():
    # Keep test deterministic by feeding a known input
    rng = np.random.default_rng(0)
    in0 = rng.random((3, 640, 640), dtype=np.float32)

    model = NcnnYolo(
        param_path="yolo11n_ncnn_model/model.ncnn.param",
        bin_path="yolo11n_ncnn_model/model.ncnn.bin",
        input_name="in0",
        output_name="out0",
        num_threads=4,
        use_vulkan=False,  # set True only if Vulkan is working on your Pi image
    )

    out0 = model.infer(in0)
    return out0


if __name__ == "__main__":
    out = test_inference()
    print(out.shape, out.dtype)
