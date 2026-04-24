import React, { useEffect, useState } from "react";
import ServerCard from "@/components/ServerCard";
import { Server, ModrinthVersion } from "@/contexts/server";
import { useServerContext } from "@/contexts/server";

export default function Home() {
  const { 
    servers, setServers, status, setStatus, activeTab, setActiveTab, 
    selected, setSelected, searchResults, searchStatus, setSearchResults, setSearchStatus 
  } = useServerContext();

  const [searchQuery, setSearchQuery] = useState("");

  const handleSelect = (server: Server) => {
    setSelected(server);
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;
    setActiveTab("search");
    setSearchStatus("loading");
    try {
      const res = await fetch(`/api/servers/search?query=${encodeURIComponent(searchQuery)}`);
      const data = await res.json();
      setSearchResults(data as ModrinthVersion[]);
      setSearchStatus("idle");
    } catch (e) {
      console.error("Search error:", e);
      setSearchStatus("error");
    }
  };

  const handleInstall = async (serverType: string) => {
    setStatus("loading");
    try {
      const res = await fetch(`/api/servers/install?server_type=${serverType}`, { method: "POST" });
      const data = await res.json();
      if (data.success) {
        alert(`Installed to ${data.file_path}`);
      } else {
        alert(`Failed: ${data.error}`);
      }
      setStatus("idle");
    } catch (e) {
      console.error("Install error:", e);
      setStatus("error");
    }
  };

  const handleDownload = async () => {
    if (!selected) return;
    try {
      const res = await fetch(
        `/api/servers/download?server_type=${selected.server_type}&version=${selected.version}&name=${selected.name}`
      );
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `${selected.name}.sh`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (e) {
      console.error("Download error:", e);
    }
  };

  useEffect(() => {
    if (activeTab === "search") return;
    const fetchServers = async () => {
      setStatus("loading");
      try {
        const res = await fetch(`/api/servers/${activeTab}`);
        const data = await res.json();
        setServers(data as Server[]);
        setStatus("idle");
      } catch (e) {
        console.error("Fetch error:", e);
        setStatus("error");
      }
    };
    fetchServers();
  }, [activeTab]);

  return (
    <div className="min-h-screen p-4 bg-gray-100">
      <div className="max-w-6xl mx-auto">
        <h1 className="text-3xl font-bold mb-8 text-gray-800">Minecraft Server Manager</h1>

        <div className="mb-6">
          <div className="flex flex-wrap gap-2 mb-4">
            <button
              className={`px-6 py-2 rounded-lg font-medium transition-colors ${
                activeTab === "java" ? "bg-blue-600 text-white shadow-md" : "bg-white text-gray-700 hover:bg-gray-50"
              }`}
              onClick={() => setActiveTab("java")}
            >
              Java Servers
            </button>
            <button
              className={`px-6 py-2 rounded-lg font-medium transition-colors ${
                activeTab === "bedrock" ? "bg-purple-600 text-white shadow-md" : "bg-white text-gray-700 hover:bg-gray-50"
              }`}
              onClick={() => setActiveTab("bedrock")}
            >
              Bedrock Servers
            </button>
          </div>

          <div className="flex gap-2 mb-4">
            <select className="px-4 py-2 rounded-lg border border-gray-300">
              <option value="paper">Paper</option>
              <option value="purpur">Purpur</option>
              <option value="fabric">Fabric</option>
              <option value="spigot">Spigot</option>
              <option value="folia">Folia</option>
            </select>
            <input
              type="text"
              placeholder="Minecraft version (e.g., 1.20.4)"
              className="px-4 py-2 rounded-lg border border-gray-300 w-48"
            />
            <button
              onClick={() => {
                const select = document.querySelector("select") as HTMLSelectElement;
                handleInstall(select.value);
              }}
              className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
            >
              Install
            </button>
          </div>
        </div>

        {activeTab !== "search" ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {servers.map((s) => (
              <ServerCard
                key={s.name + s.version}
                server={{ ...s, status: selected?.name === s.name ? "selected" : "default" }}
                onSelect={handleSelect}
              />
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {searchResults.map((r, i) => (
              <div
                key={i}
                className="border rounded-lg p-4 shadow-sm bg-white hover:shadow-md cursor-pointer transition-all"
                onClick={() => setSelected({
                  name: r.file_name.replace(".jar", ""),
                  version: r.version_name,
                  server_type: "java",
                })}
              >
                <h3 className="text-lg font-semibold">{r.file_name}</h3>
                <p className="text-sm text-gray-500">{r.version_name}</p>
                <p className="text-sm text-gray-600 mt-2 line-clamp-2">{r.description}</p>
              </div>
            ))}
          </div>
        )}

        {(status === "loading" || searchStatus === "loading") && (
          <div className="mt-8 text-center">
            <p className="text-gray-600">Loading...</p>
          </div>
        )}
        {(status === "error" || searchStatus === "error") && (
          <div className="mt-8 text-center">
            <p className="text-red-500 bg-red-100 inline-block px-4 py-2 rounded">Failed to load.</p>
          </div>
        )}

        {selected && activeTab !== "search" && (
          <div className="mt-8 p-6 bg-white rounded-xl shadow-lg border border-gray-200">
            <h2 className="text-2xl font-bold mb-4 text-gray-800">Selected Server</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <span className="text-sm text-gray-500">Name</span>
                <p className="text-lg font-semibold">{selected.name}</p>
              </div>
              <div>
                <span className="text-sm text-gray-500">Version</span>
                <p className="text-lg font-semibold">{selected.version}</p>
              </div>
              <div>
                <span className="text-sm text-gray-500">Type</span>
                <p className="text-lg font-semibold">{selected.server_type}</p>
              </div>
            </div>
            <button
              onClick={handleDownload}
              className="mt-4 px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
            >
              Download Launch Script
            </button>
          </div>
        )}
      </div>
    </div>
  );
}