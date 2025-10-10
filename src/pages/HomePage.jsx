import { useEffect, useRef, useState } from "react";
import axios from "axios";

export default function HomePage() {
  const videoRef = useRef(null);
  const [detectedName, setDetectedName] = useState("");
  const [showNotification, setShowNotification] = useState(false);
  const recognitionIntervalRef = useRef(null);

  // Start webcam
  useEffect(() => {
    navigator.mediaDevices.getUserMedia({ video: true }).then(stream => {
      if (videoRef.current) videoRef.current.srcObject = stream;
      videoRef.current.play();
    });
  }, []);

  // Recognition loop
  useEffect(() => {
    recognitionIntervalRef.current = setInterval(async () => {
      if (!videoRef.current || videoRef.current.readyState !== 4) return;

      // Capture frame
      const canvas = document.createElement("canvas");
      canvas.width = videoRef.current.videoWidth;
      canvas.height = videoRef.current.videoHeight;
      const ctx = canvas.getContext("2d");
      ctx.drawImage(videoRef.current, 0, 0, canvas.width, canvas.height);
      const imageData = canvas.toDataURL("image/jpeg");

      try {
        const res = await axios.post("http://localhost:5000/recognize", { image: imageData });
        const faces = res.data.faces;

        if (faces.length > 0 && faces[0].name !== "Unknown") {
          const name = faces[0].name;

          // Pause video
          videoRef.current.pause();

          // Show notification
          setDetectedName(name);
          setShowNotification(true);

          // Hide notification after 1s and resume
          setTimeout(() => {
            setShowNotification(false);
            videoRef.current.play();
          }, 1000);
        }

      } catch (err) {
        console.log("Recognition error:", err);
      }
    }, 1000);

    return () => clearInterval(recognitionIntervalRef.current);
  }, []);

  return (
    <div style={{
      width: "100vw",
      height: "100vh",
      backgroundColor: "black",
      display: "flex",
      justifyContent: "center",
      alignItems: "center",
      overflow: "hidden",
      position: "relative"
    }}>
      <video
        ref={videoRef}
        autoPlay
        playsInline
        style={{
          width: "100%",
          height: "100%",
          objectFit: "contain",
          display: "block", 
        }}
      />

      {/* Notification */}
      {showNotification && (
        <div style={{
          position: "absolute",
          top: "20%",
          left: "50%",
          transform: "translateX(-50%)",
          backgroundColor: "rgba(0,0,0,0.7)",
          color: "lime",
          padding: "20px 40px",
          borderRadius: "12px",
          fontSize: "2rem",
          fontWeight: "bold",
          display: "flex",
          alignItems: "center",
          gap: "10px",
          animation: "fadeInOut 1s ease-in-out"
        }}>
          <span>{detectedName}</span>
          <span>✔️</span>
        </div>
      )}

      {/* Animation keyframes */}
      <style>
        {`
          @keyframes fadeInOut {
            0% { opacity: 0; transform: translate(-50%, -20px); }
            10% { opacity: 1; transform: translate(-50%, 0); }
            90% { opacity: 1; transform: translate(-50%, 0); }
            100% { opacity: 0; transform: translate(-50%, -20px); }
          }
        `}
      </style>
    </div>
  );
}
