import { type HTMLMotionProps, motion, useSpring } from "framer-motion";
import { type MouseEvent, useRef, useState } from "react";
import { cn } from "@/lib/utils";

export interface MagnetButtonProps extends Omit<HTMLMotionProps<"button">, "ref"> {
  magnetStrength?: number;
  activeScale?: number;
}

export function MagnetButton({
  children,
  className,
  magnetStrength = 0.35,
  activeScale = 1.03,
  disabled,
  onClick,
  type = "button",
  ...props
}: MagnetButtonProps) {
  const ref = useRef<HTMLButtonElement>(null);
  const [isHovered, setIsHovered] = useState(false);

  const springConfig = { damping: 15, stiffness: 150, mass: 0.1 };
  const x = useSpring(0, springConfig);
  const y = useSpring(0, springConfig);

  const handleMouseMove = (e: MouseEvent<HTMLButtonElement>) => {
    if (disabled || !ref.current) return;
    const { clientX, clientY } = e;
    const { left, top, width, height } = ref.current.getBoundingClientRect();
    const centerX = left + width / 2;
    const centerY = top + height / 2;
    const distanceX = (clientX - centerX) * magnetStrength;
    const distanceY = (clientY - centerY) * magnetStrength;
    x.set(distanceX);
    y.set(distanceY);
  };

  const handleMouseLeave = () => {
    setIsHovered(false);
    x.set(0);
    y.set(0);
  };

  const handleMouseEnter = () => {
    if (!disabled) setIsHovered(true);
  };

  return (
    <motion.button
      ref={ref}
      type={type}
      style={{ x, y }}
      whileTap={{ scale: disabled ? 1 : 0.97 }}
      animate={{ scale: isHovered && !disabled ? activeScale : 1 }}
      onMouseMove={handleMouseMove}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
      onClick={onClick}
      disabled={disabled}
      className={cn(
        "relative inline-flex items-center justify-center font-medium rounded-xl transition-colors duration-200 outline-none focus-visible:ring-2 focus-visible:ring-indigo-400 focus-visible:ring-offset-2 focus-visible:ring-offset-black disabled:pointer-events-none disabled:opacity-50 select-none",
        className
      )}
      {...props}
    >
      {children}
    </motion.button>
  );
}
