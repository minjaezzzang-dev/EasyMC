import React from "react";
import { Server } from "@/contexts/server";

interface ServerCardProps {
  server: Server & { status?: "selected" | "default" };
  onSelect: (server: Server) => void;
}

export default function ServerCard({ server, onSelect }: ServerCardProps) {
  const className = "border rounded-lg p-4 shadow-sm hover:shadow-md cursor-pointer transition-all";
  const statusClass = server.status === "selected" ? "bg-blue-200 ring-2 ring-blue-500" : "bg-white hover:border-gray-300";

  return (
    <div
      className={`${className} ${statusClass}`}
      onClick={() => onSelect(server)}
    >
      <h3 className="text-lg font-semibold">{server.name}</h3>
      <p className="text-sm text-gray-500">
        {server.version} • {server.server_type}
      </p>
    </div>
  );
}