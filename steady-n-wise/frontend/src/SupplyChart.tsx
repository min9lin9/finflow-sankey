import { useEffect, useRef } from "react";

import type { SupplyResponse } from "./api";

interface SupplyChartProps {
  response: SupplyResponse | null;
}

export function SupplyChart({ response }: SupplyChartProps) {
  const ref = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (!ref.current || !response) {
      return;
    }
    let disposed = false;
    let disposeChart: (() => void) | undefined;

    import("./chartRuntime").then(({ renderSupplyChart }) => {
      if (!ref.current || disposed) {
        return;
      }
      const chart = renderSupplyChart(ref.current, response);
      const resize = () => chart.resize();
      window.addEventListener("resize", resize);
      disposeChart = () => {
        window.removeEventListener("resize", resize);
        chart.dispose();
      };
    });

    return () => {
      disposed = true;
      disposeChart?.();
    };
  }, [response]);

  return (
    <div className="chart-wrap">
      <div className="chart" ref={ref} role="img" aria-label="시가총액과 수급오실레이터 차트" />
    </div>
  );
}
