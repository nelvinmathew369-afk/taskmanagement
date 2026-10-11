import React from "react";
import { Layers, Clock, Loader2, CheckCircle2 } from "lucide-react";

export default function TaskSummaryCards({ summary, onFilterByStatus }) {
  const cards = [
    {
      title: "Total Tasks",
      count: summary?.total ?? 0,
      icon: <Layers size={22} />,
      iconClass: "icon-total",
      statusKey: null,
    },
    {
      title: "Pending",
      count: summary?.pending ?? 0,
      icon: <Clock size={22} />,
      iconClass: "icon-pending",
      statusKey: "Pending",
    },
    {
      title: "In Progress",
      count: summary?.in_progress ?? 0,
      icon: <Loader2 size={22} />,
      iconClass: "icon-progress",
      statusKey: "In Progress",
    },
    {
      title: "Completed",
      count: summary?.completed ?? 0,
      icon: <CheckCircle2 size={22} />,
      iconClass: "icon-completed",
      statusKey: "Completed",
    },
  ];

  return (
    <div className="metrics-grid">
      {cards.map((card, idx) => (
        <div
          key={idx}
          className="metric-card"
          onClick={() => card.statusKey !== null && onFilterByStatus?.(card.statusKey)}
          style={{ cursor: card.statusKey !== null ? "pointer" : "default" }}
          title={card.statusKey ? `Click to filter by ${card.statusKey}` : ""}
        >
          <div>
            <div className="metric-title">{card.title}</div>
            <div className="metric-value">{card.count}</div>
          </div>
          <div className={`metric-icon-wrap ${card.iconClass}`}>
            {card.icon}
          </div>
        </div>
      ))}
    </div>
  );
}
