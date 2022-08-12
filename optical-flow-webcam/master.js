navigator.getMedia = (navigator.getUserMedia ||
    navigator.webkitGetUserMedia ||
    navigator.mozGetUserMedia ||
    navigator.msGetUserMedia);

async function load_effect() {

    var video_loaded = false;
    var image_loaded = false;

    const size = 256;
    const width = size;
    const height = size;

    const video_container = document.getElementById("container-video");
    const video = document.createElement("video");
    video.muted = true;
    video.loop = true;
    video.style.objectFit = "cover";
    video.setAttribute("width", size);
    video.setAttribute("height", size);
    video.addEventListener("canplay", () => {
        if (!video_loaded) {
            console.log("Video is loaded");
            video_container.innerHTML = "";
            video_container.appendChild(video);
            if (image_loaded) start_effect();
        }
        video_loaded = true;
    }, false);

    const image_container = document.getElementById("container-image");
    const image = new Image();
    const image_canvas = document.createElement("canvas");
    image_canvas.width = width;
    image_canvas.height = height;
    const image_canvas_context = image_canvas.getContext("2d");
    image.crossOrigin = "anonymous";
    image.addEventListener("load", () => {
        if (!image_loaded) {
            console.log("Image is loaded");
            image_container.innerHTML = "";            
            image_container.appendChild(image_canvas);
            const target_ratio = width / height;
            const current_ratio = image.width / image.height;
            var cropped_width = image.width;
            var cropped_height = image.height;
            if (target_ratio > current_ratio) {
                // Crop vertically
                cropped_height = cropped_width / target_ratio;
            } else if (target_ratio < current_ratio) {
                // Crop horizontaly
                cropped_width = target_ratio * cropped_height;
            }
            image_canvas_context.drawImage(image, (image.width - cropped_width) / 2, (image.height - cropped_height) / 2, cropped_width, cropped_height, 0, 0, width, height);
            context.drawImage(image, (image.width - cropped_width) / 2, (image.height - cropped_height) / 2, cropped_width, cropped_height, 0, 0, width, height);
            if (video_loaded) start_effect();
        }
        image_loaded = true;
    }, false);

    const canvas = document.getElementById("canvas");
    canvas.width = width;
    canvas.height = height;
    const context = canvas.getContext("2d");
    var image_data;
    var cap;

    async function start_effect() {
        console.log("Both media loaded, starting the effect");

        document.getElementById("button-reset").removeAttribute("disabled");
        document.getElementById("button-download").removeAttribute("disabled");

        function takepicture() {
            let frame = new cv.Mat(height, width, cv.CV_8UC4);
            let frame_gray = new cv.Mat();
            cap.read(frame);
            cv.cvtColor(frame, frame_gray, cv.COLOR_RGBA2GRAY);
            return frame_gray;
        }
        
        cap = new cv.VideoCapture(video);
        let reference = takepicture();
        image_data = context.getImageData(0, 0, width, height);
        while (true) {
            let current = takepicture();
            let flow = new cv.Mat();
            cv.calcOpticalFlowFarneback(reference, current, flow, 0.5, 3, 15, 3, 5, 1.2, 0);
            let image_data_copy = [...image_data.data];
            for (let i = 0; i < height; i++) {
                for (let j = 0; j < width; j++) {
                    let k = (i * width + j);
                    let ii = i + Math.round(flow.data32F[k * 2]);
                    let jj = j + Math.round(flow.data32F[k * 2 + 1]);
                    image_data.data[(ii * width + jj) * 4] = image_data_copy[(i * width + j) * 4];
                    image_data.data[(ii * width + jj) * 4 + 1] = image_data_copy[(i * width + j) * 4 + 1];
                    image_data.data[(ii * width + jj) * 4 + 2] = image_data_copy[(i * width + j) * 4 + 2];
                    image_data.data[(ii * width + jj) * 4 + 3] = image_data_copy[(i * width + j) * 4 + 3];
                }
            }
            context.putImageData(image_data, 0, 0);
            await new Promise(x => requestAnimationFrame(x));
            current.copyTo(reference);
        }

    }

    async function load_video_webcam() {
        console.log("Loading video from the webcam");
        navigator.getMedia({ video: true, audio: false }, (stream) => {
            if (navigator.mozGetUserMedia) {
                video.srcObject = stream;
            } else {
                video.src = vendorURL.createObjectURL(stream);
            }
            video.play();
        }, (err) => {
            alert(err);
            console.error(err);
            document.getElementById("button-video-modal").disabled = false;
        });
        while (!video_loaded) { await new Promise(resolve => setTimeout(resolve, 10)); }
    }

    async function load_video_url(video_url) {
        console.log("Loading video from a URL:", video_url);
        video.src = video_url;
        video.play();
    }

    async function load_video_file(video_file) {
        console.log("Loading video from a file:", video_file);
        video.src = URL.createObjectURL(video_file);
        video.play();
    }

    document.getElementById("button-video-webcam").addEventListener("click", () => {
        document.getElementById("button-video-modal").disabled = true;
        closeModal("modal-load-video");
        load_video_webcam();
    });

    document.getElementById("button-video-load").addEventListener("click", () => {
        let video_url = document.getElementById("input-video-url").value;
        let video_files = document.getElementById("input-video-file").files;
        if (video_url != "") {
            load_video_url(video_url);
        } else if (video_files.length > 0) {
            load_video_file(video_files[0]);
        } else {
            alert("Please specify one source!");
            return;
        }
        document.getElementById("button-video-modal").disabled = true;
        closeModal("modal-load-video");
    });

    document.getElementById("button-image-random").addEventListener("click", () => {
        console.log("Loading random image");
        image.src = `https://picsum.photos/${ width }/${ height }`;
        if (document.getElementById("button-image-modal")) {
            document.getElementById("button-image-modal").disabled = true;
        }
        closeModal("modal-load-image");
    });

    document.getElementById("button-image-load").addEventListener("click", () => {
        let image_url = document.getElementById("input-image-url").value;
        let image_files = document.getElementById("input-image-file").files;
        if (image_url != "") {
            console.log("Loading image from a URL:", image_url);
            image.src = image_url;
        } else if (image_files.length > 0) {
            console.log("Loading image from a file:", image_files[0]);
            image.src = URL.createObjectURL(image_files[0]);
        } else {
            alert("Please specify one source!");
            return;
        }
        document.getElementById("button-image-modal").disabled = true;
        closeModal("modal-load-image");
    });

    document.getElementById("button-reset").addEventListener("click", () => {
        image_data = image_canvas_context.getImageData(0, 0, width, height);
    });

    document.getElementById("button-download").addEventListener("click", () => {
        const link = document.createElement("a");
        link.download = `${ Date.now() }.png`;
        link.href = canvas.toDataURL();
        link.click();
    });

}

window.addEventListener("load", load_effect);
