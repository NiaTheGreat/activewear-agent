"use client";

import { useEffect, useState } from "react";
import { motion, useSpring, useTransform } from "framer-motion";

interface ScoreAnimatedNumberProps {
  value: number;
  duration?: number;
  decimals?: number;
}

export function ScoreAnimatedNumber({
  value,
  duration = 1,
  decimals = 0,
}: ScoreAnimatedNumberProps) {
  const spring = useSpring(0, { duration: duration * 1000, bounce: 0 });
  const display = useTransform(spring, (v) => v.toFixed(decimals));
  const [displayValue, setDisplayValue] = useState("0");

  useEffect(() => {
    spring.set(value);
  }, [spring, value]);

  useEffect(() => {
    const unsubscribe = display.on("change", (v) => setDisplayValue(v));
    return unsubscribe;
  }, [display]);

  return <motion.span>{displayValue}</motion.span>;
}
