import type { AppProps } from "next/app";
import "@/styles/globals.css";
import { ServerContext, Server, ModrinthVersion } from "@/contexts/server";
import { useState, ReactNode } from "react";

interface AppPropsWithServer extends AppProps<{
  servers: Server[];
}> {}

export default function MyApp({ Component, pageProps }: AppPropsWithServer) {
  const [servers, setServers] = useState<Server[]>([]);
  const [status, setStatus] = useState<"loading" | "error" | "idle">("idle");
  const [activeTab, setActiveTab] = useState<"java" | "bedrock" | "search">("java");
  const [selected, setSelected] = useState<Server | null>(null);
  const [searchResults, setSearchResults] = useState<ModrinthVersion[]>([]);
  const [searchStatus, setSearchStatus] = useState<"loading" | "error" | "idle">("idle");

  const value = {
    servers,
    setServers,
    status,
    setStatus,
    activeTab,
    setActiveTab,
    selected,
    setSelected,
    searchResults,
    searchStatus,
    setSearchResults,
    setSearchStatus,
  };

  return (
    <ServerContext.Provider value={value}>
      <Component {...pageProps} />
    </ServerContext.Provider>
  );
}