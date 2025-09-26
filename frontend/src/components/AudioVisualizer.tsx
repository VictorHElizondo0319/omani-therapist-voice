'use client';

import { motion } from 'framer-motion';

interface AudioVisualizerProps {
  level: number;
  isActive?: boolean;
  color?: string;
}

export function AudioVisualizer({ 
  level, 
  isActive = true, 
  color = '#3b82f6' 
}: AudioVisualizerProps) {
  const bars = Array.from({ length: 8 }, (_, i) => i);
  
  const getBarHeight = (index: number) => {
    // Create a wave-like pattern based on audio level and bar position
    const baseHeight = Math.max(4, (level / 100) * 20);
    const waveOffset = Math.sin((index / bars.length) * Math.PI * 2 + Date.now() / 100) * 2;
    return baseHeight + waveOffset;
  };

  return (
    <div className="flex items-center space-x-1 space-x-reverse">
      {bars.map((index) => (
        <motion.div
          key={index}
          className="bg-primary-500 rounded-full"
          style={{
            width: '3px',
            height: `${getBarHeight(index)}px`,
            backgroundColor: color
          }}
          animate={{
            height: isActive ? `${getBarHeight(index)}px` : '4px',
            opacity: isActive ? 1 : 0.3
          }}
          transition={{
            duration: 0.1,
            ease: 'easeOut'
          }}
        />
      ))}
    </div>
  );
}
