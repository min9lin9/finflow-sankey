import { LineChart } from "echarts/charts";
import {
  DataZoomComponent,
  GridComponent,
  TooltipComponent,
  type TooltipComponentOption,
} from "echarts/components";
import * as echarts from "echarts/core";
import { CanvasRenderer } from "echarts/renderers";

import type { SupplyResponse } from "./api";

echarts.use([LineChart, GridComponent, TooltipComponent, DataZoomComponent, CanvasRenderer]);

export function renderSupplyChart(element: HTMLDivElement, response: SupplyResponse) {
  const styles = getComputedStyle(document.documentElement);
  const marketColor = styles.getPropertyValue("--chart-market-cap").trim();
  const oscillatorColor = styles.getPropertyValue("--chart-oscillator").trim();
  const axisColor = styles.getPropertyValue("--text-secondary").trim();
  const chart = echarts.init(element, undefined, { renderer: "canvas" });

  chart.setOption({
    animationDuration: 420,
    color: [marketColor, oscillatorColor],
    tooltip: { trigger: "axis" } satisfies TooltipComponentOption,
    grid: { left: 64, right: 64, top: 32, bottom: 72 },
    xAxis: {
      type: "category",
      data: response.data.map((point) => point.date),
      axisLabel: { color: axisColor },
    },
    yAxis: [
      {
        type: "value",
        name: "시가총액",
        axisLabel: {
          color: axisColor,
          formatter: (value: number) => `${Math.round(value / 1_000_000_000_000)}조`,
        },
      },
      {
        type: "value",
        name: "오실레이터",
        axisLabel: { color: axisColor },
      },
    ],
    dataZoom: [{ type: "inside" }, { type: "slider", height: 24, bottom: 24 }],
    series: [
      {
        name: "시가총액",
        type: "line",
        smooth: true,
        showSymbol: false,
        data: response.data.map((point) => point.market_cap),
      },
      {
        name: "수급오실레이터",
        type: "line",
        smooth: true,
        showSymbol: false,
        yAxisIndex: 1,
        areaStyle: { opacity: 0.08 },
        data: response.data.map((point) => point.oscillator),
      },
    ],
  });

  return chart;
}
