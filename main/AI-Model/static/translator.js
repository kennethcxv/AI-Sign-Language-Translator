// // Your existing code
// const videoElement = document.getElementById('camera');
// const webcam = new Webcam(videoElement, 'user');
// const audioElement = document.querySelector('audio');
//
// function onOpenCvReady() {
//     document.getElementById('status').innerHTML = 'OpenCV.js is ready.';
//     let video = document.getElementById("liveVideo");
//     if (navigator.mediaDevices.getUserMedia) {
//         navigator.mediaDevices.getUserMedia({ video: true })
//             .then(function (stream) {
//                 video.srcObject = stream;
//             })
//             .catch(function (error) {
//                 console.log("Error accessing webcam:", error);
//             });
//     }
// }
//
// const transcriptArea = document.getElementById('transcript');
// const audioBox = document.querySelector('.audio-box');
//
// async function fetchTranscriptAndAudio() {
//     try {
//         const response = await fetch('/get-transcript-and-audio'); // Assuming you have an endpoint named 'get-transcript-and-audio'
//         const data = await response.json();
//
//         if (data.transcript) {
//             transcriptArea.value = data.transcript;
//         }
//
//         if (data.audio) {
//             // Assuming you have an audio element to play the audio
//             audioElement.src = data.audio;
//             audioElement.play();
//
//             // Display the audio bars animation
//             audioBox.classList.add('playing');
//             audioElement.addEventListener('ended', () => {
//                 audioBox.classList.remove('playing');
//             });
//         }
//     } catch (error) {
//         console.error("Error fetching the transcript and audio:", error);
//     }
// }
//
// fetchTranscriptAndAudio();