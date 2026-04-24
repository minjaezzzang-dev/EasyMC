import { createContext, useState, useContext, ReactNode, Dispatch, SetStateAction } from "react";

export interface Server {
  name: string;
  version: string;
  server_type: string;
  jar_path?: string;
}

export interface ModrinthVersion {
  project_id: string;
  version_name: string;
  file_name: string;
  description: string;
  download_url: string;
}

type Status = "loading" | "error" | "idle";
type Tab = "java" | "bedrock" | "search";

export const ServerContext = createContext<{
  servers: Server[];
  setServers: Dispatch<SetStateAction<Server[]>>;
  status: Status;
  setStatus: Dispatch<SetStateAction<Status>>;
  activeTab: Tab;
  setActiveTab: Dispatch<SetStateAction<Tab>>;
  selected: Server | null;
  setSelected: Dispatch<SetStateAction<Server | null>>;
  searchResults: ModrinthVersion[];
  searchStatus: Status;
  setSearchResults: Dispatch<SetStateAction<ModrinthVersion[]>>;
  setSearchStatus: Dispatch<SetStateAction<Status>>;
} | null>(null);

export function useServerContext() {
  const context = useContext(ServerContext);
  if (!context) {
    throw new Error("useServerContext must be used within a ServerProvider");
  }
  return context;
}