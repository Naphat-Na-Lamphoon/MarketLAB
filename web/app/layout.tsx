import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "MarketLab",
  description: "Experiment-driven product validation",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
