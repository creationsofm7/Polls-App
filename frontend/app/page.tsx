"use client";

import { Button } from "@/components/ui/button";
import Wall from "@/components/wall";
import MyPolls from "@/components/myPolls";
import CreatePoll from "@/components/createPolls";
import { useCallback, useState } from "react";
import { useAuthStore } from "@/stores/auth-store";
import { AuthDialog } from "@/components/auth/auth-dialog";
import { LogoutButton } from "@/components/auth/logout-button";
import { BarChart3, PlusCircle, User } from "lucide-react";

export default function Home() {
  const [activeTab, setActiveTab] = useState("wall");
  const token = useAuthStore((state) => state.token);

  const handlePollCreated = useCallback(() => {
    setActiveTab("myPolls");
  }, []);

  return (
    <>
      <header className="bg-white dark:bg-zinc-900 border-b border-zinc-200 dark:border-zinc-800 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* Logo and Brand */}
            <div className="flex items-center space-x-3">
              <div className="flex items-center justify-center w-10 h-10 bg-blue-600 rounded-lg">
                <BarChart3 className="h-6 w-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-zinc-900 dark:text-zinc-100">Polls</h1>
                <p className="text-xs text-zinc-500 dark:text-zinc-400">Interactive Polling Platform</p>
              </div>
            </div>

            {/* Auth Section */}
            <div className="flex items-center">
              {token ? <LogoutButton /> : <AuthDialog />}
            </div>
          </div>
        </div>
      </header>
      
      <main className="min-h-screen bg-zinc-50 dark:bg-zinc-950">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 lg:py-12">
          <div className="lg:flex lg:items-start lg:gap-10">
            <aside className="hidden lg:block lg:w-64 lg:flex-shrink-0">
              <nav className="sticky top-28 flex flex-col gap-2 rounded-xl border border-zinc-200 bg-white p-4 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
                <Button
                  onClick={() => setActiveTab("wall")}
                  variant={activeTab === "wall" ? "default" : "ghost"}
                  className="w-full justify-start space-x-2"
                >
                  <BarChart3 className="h-4 w-4" />
                  <span>All Polls</span>
                </Button>
                <Button
                  onClick={() => setActiveTab("myPolls")}
                  variant={activeTab === "myPolls" ? "default" : "ghost"}
                  className="w-full justify-start space-x-2"
                >
                  <User className="h-4 w-4" />
                  <span>My Polls</span>
                </Button>
                <Button
                  onClick={() => setActiveTab("createPoll")}
                  variant={activeTab === "createPoll" ? "default" : "ghost"}
                  className="w-full justify-start space-x-2"
                >
                  <PlusCircle className="h-4 w-4" />
                  <span>Create Poll</span>
                </Button>
              </nav>
            </aside>

            <section className="flex-1 pb-24 lg:pb-0">
              {activeTab === "wall" && <Wall isActive={true} />}
              {activeTab === "myPolls" && <MyPolls isActive={true} />}
              {activeTab === "createPoll" && <CreatePoll onPollCreated={handlePollCreated} />}
            </section>
          </div>
        </div>
      </main>

      <nav className="fixed bottom-0 left-0 right-0 z-20 border-t border-zinc-200 bg-white/95 backdrop-blur supports-[backdrop-filter]:bg-white/75 dark:border-zinc-800 dark:bg-zinc-900/95 dark:supports-[backdrop-filter]:bg-zinc-900/75 lg:hidden">
        <div className="mx-auto flex max-w-7xl items-center justify-around px-2 py-2">
          <Button
            onClick={() => setActiveTab("wall")}
            variant="ghost"
            className={`flex-1 flex-col items-center gap-1 py-2 text-xs font-medium ${
              activeTab === "wall"
                ? "text-blue-600 dark:text-blue-400"
                : "text-zinc-500 dark:text-zinc-400"
            }`}
          >
            <BarChart3 className="h-5 w-5" />
            <span>All Polls</span>
          </Button>
          <Button
            onClick={() => setActiveTab("myPolls")}
            variant="ghost"
            className={`flex-1 flex-col items-center gap-1 py-2 text-xs font-medium ${
              activeTab === "myPolls"
                ? "text-blue-600 dark:text-blue-400"
                : "text-zinc-500 dark:text-zinc-400"
            }`}
          >
            <User className="h-5 w-5" />
            <span>My Polls</span>
            
          </Button>
          <Button
            onClick={() => setActiveTab("createPoll")}
            variant="ghost"
            className={`flex-1 flex-col items-center gap-1 py-2 text-xs font-medium ${
              activeTab === "createPoll"
                ? "text-blue-600 dark:text-blue-400"
                : "text-zinc-500 dark:text-zinc-400"
            }`}
          >
            <PlusCircle className="h-5 w-5" />
            <span>Create</span>
          </Button>
        </div>
      </nav>
    </>
  );
}
