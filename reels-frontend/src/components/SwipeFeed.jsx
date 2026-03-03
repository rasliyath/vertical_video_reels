// src/components/SwipeFeed.jsx
import { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import ReelPlayer from "./ReelPlayer";

export default function SwipeFeed({ reels, onHeadlineUpdate }) {
  const [currentIndex, setCurrentIndex] = useState(0);
  const containerRef = useRef(null);
  const touchStartY = useRef(0);
  const lastSwipeTime = useRef(0);

  const goNext = () => {
    if (currentIndex < reels.length - 1) {
      setCurrentIndex((i) => i + 1);
    }
  };

  const goPrev = () => {
    if (currentIndex > 0) {
      setCurrentIndex((i) => i - 1);
    }
  };

  // Keyboard navigation
  useEffect(() => {
    const handleKey = (e) => {
      if (e.key === "ArrowDown" || e.key === "ArrowRight" || e.key === " ") {
        e.preventDefault();
        goNext();
      }
      if (e.key === "ArrowUp" || e.key === "ArrowLeft") {
        e.preventDefault();
        goPrev();
      }
    };
    window.addEventListener("keydown", handleKey);
    return () => window.removeEventListener("keydown", handleKey);
  }, [currentIndex, reels.length]);

  // Touch handlers for swipe
  const handleTouchStart = (e) => {
    touchStartY.current = e.touches[0].clientY;
  };

  const handleTouchEnd = (e) => {
    const touchEndY = e.changedTouches[0].clientY;
    const deltaY = touchStartY.current - touchEndY;
    const now = Date.now();
    
    // Prevent multiple swipes in quick succession
    if (now - lastSwipeTime.current < 500) return;
    
    // Swipe threshold
    if (Math.abs(deltaY) > 50) {
      lastSwipeTime.current = now;
      if (deltaY > 0) {
        // Swipe up = next
        goNext();
      } else {
        // Swipe down = prev
        goPrev();
      }
    }
  };

  // Mouse wheel for desktop
  useEffect(() => {
    const handleWheel = (e) => {
      const now = Date.now();
      if (now - lastSwipeTime.current < 500) return;
      
      if (e.deltaY > 30) {
        lastSwipeTime.current = now;
        goNext();
      } else if (e.deltaY < -30) {
        lastSwipeTime.current = now;
        goPrev();
      }
    };
    
    const el = containerRef.current;
    if (el) {
      el.addEventListener("wheel", handleWheel, { passive: true });
    }
    return () => {
      if (el) el.removeEventListener("wheel", handleWheel);
    };
  }, [currentIndex, reels.length]);

  if (!reels.length) {
    return (
      <div style={styles.empty}>
        <div style={{ fontSize: "48px", marginBottom: "16px" }}>🎬</div>
        <p style={{ color: "#666", fontSize: "16px" }}>No reels yet</p>
        <p style={{ color: "#888", fontSize: "13px", marginTop: "8px" }}>
          Generate some reels to see them here
        </p>
      </div>
    );
  }

  return (
    <div ref={containerRef} style={styles.container}>
      {/* Centered reel container - Instagram-like width */}
      <div style={styles.reelCenterContainer}>
        <div 
          style={styles.swipeContainer}
          onTouchStart={handleTouchStart}
          onTouchEnd={handleTouchEnd}
        >
          <AnimatePresence mode="wait">
            <motion.div
              key={currentIndex}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.15 }}
              style={styles.reelWrapper}
            >
              <ReelPlayer
                reel={reels[currentIndex]}
                isActive={true}
                currentIndex={currentIndex}
                totalReels={reels.length}
                onHeadlineUpdate={(updated) => onHeadlineUpdate(updated)}
              />
            </motion.div>
          </AnimatePresence>
        </div>

        {/* Navigation indicators - click to go to specific reel */}
        <div style={styles.indicators}>
          {reels.map((_, i) => (
            <div
              key={i}
              onClick={() => setCurrentIndex(i)}
              style={{
                ...styles.indicator,
                background: i === currentIndex ? "#fff" : "rgba(255,255,255,0.4)",
                transform: i === currentIndex ? "scale(1.2)" : "scale(1)",
              }}
            />
          ))}
        </div>

        {/* Counter */}
        <div style={styles.counter}>
          {currentIndex + 1} / {reels.length}
        </div>
      </div>
    </div>
  );
}

const styles = {
  container: {
    position: "relative",
    width: "100%",
    height: "calc(100vh - 180px)",
    minHeight: "600px",
    background: "#000",
    borderRadius: "12px",
    overflow: "hidden",
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
  },
  reelCenterContainer: {
    position: "relative",
    height: "100%",
    aspectRatio: "9/16",
    maxHeight: "100%",
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
  },
  swipeContainer: {
    width: "100%",
    height: "100%",
    position: "relative",
    borderRadius: "8px",
    overflow: "hidden",
  },
  reelWrapper: {
    width: "100%",
    height: "100%",
    position: "relative",
  },
  indicators: {
    position: "absolute",
    right: "12px",
    top: "50%",
    transform: "translateY(-50%)",
    display: "flex",
    flexDirection: "column",
    gap: "8px",
    zIndex: 10,
  },
  indicator: {
    width: "5px",
    height: "5px",
    borderRadius: "50%",
    cursor: "pointer",
    transition: "all 0.2s",
  },
  counter: {
    position: "absolute",
    bottom: "16px",
    left: "50%",
    transform: "translateX(-50%)",
    color: "rgba(255,255,255,0.7)",
    fontSize: "13px",
    fontWeight: "500",
    zIndex: 10,
  },
  empty: {
    height: "calc(100vh - 180px)",
    minHeight: "500px",
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    justifyContent: "center",
    background: "#f9f9f9",
    borderRadius: "12px",
  },
};
