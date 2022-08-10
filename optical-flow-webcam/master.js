navigator.getMedia = (navigator.getUserMedia ||
    navigator.webkitGetUserMedia ||
    navigator.mozGetUserMedia ||
    navigator.msGetUserMedia);

async function start_optical_flow_effect() {

    var streaming = false;
    const width = 256;
    var height;
    const video = document.getElementById("video");
    const canvas = document.getElementById("canvas");
    const context_image = canvas.getContext("2d");
    var cap;

    async function load_webcam() {
        navigator.getMedia({ video: true, audio: false }, (stream) => {
            if (navigator.mozGetUserMedia) {
                video.srcObject = stream;
            } else {
                video.src = vendorURL.createObjectURL(stream);
            }
            video.play();
        }, (err) => {
            console.log("An error occured! " + err);
        });

        video.addEventListener("canplay", function(ev) {
            if (!streaming) {
                height = video.videoHeight / (video.videoWidth / width);
                video.setAttribute('width', width);
                video.setAttribute('height', height);
                streaming = true;
                cap = new cv.VideoCapture(video);
            }
        }, false);

        while (!streaming) {
            await new Promise(resolve => setTimeout(resolve, 10));
        }
    }

    async function load_image() {
        canvas.style.imageRendering = "crisp-edges";
        const image = new Image();
        image.crossOrigin = "anonymous";
        image.src = `https://picsum.photos/${ width }/${ height }`;
        await image.decode();
        canvas.width = width;
        canvas.height = height;
        context_image.drawImage(image, 0, 0, image.width, image.height, 0, 0, width, height);
    }

    await load_webcam();
    await load_image();
    // await Promise.all([load_webcam(), load_image()]);

    function takepicture() {
        let frame = new cv.Mat(height, width, cv.CV_8UC4);
        let frame_gray = new cv.Mat();
        cap.read(frame);
        cv.cvtColor(frame, frame_gray, cv.COLOR_RGBA2GRAY);
        return frame_gray;
    }

    let reference = takepicture();
    var image_data = context_image.getImageData(0, 0, width, height);
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
        context_image.putImageData(image_data, 0, 0);
        await new Promise(x => requestAnimationFrame(x));
        current.copyTo(reference);
    }

}

window.addEventListener("load", start_optical_flow_effect);