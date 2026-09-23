"use client";

import "./globals.css";
import { useEffect } from "react";

export const metadata = { title: "ARANYA", description: "The digital jungle for real-world work." };

export default function RootLayout({children}:{children:React.ReactNode}){
  useEffect(() => {
    if ("serviceWorker" in navigator) navigator.serviceWorker.register("/sw.js").catch(() => {});
  }, []);
  return <html lang="en"><head><link rel="manifest" href="/manifest.webmanifest" /><meta name="theme-color" content="#102016" /></head><body>{children}</body></html>;
}
