import { Link, Route, Routes } from "react-router-dom";
import { GraduationCap } from "lucide-react";

import JobPage from "@/pages/JobPage";
import UploadPage from "@/pages/UploadPage";

export default function App() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-50 to-slate-100">
      <header className="border-b bg-white/70 backdrop-blur">
        <div className="container flex h-16 items-center gap-2">
          <Link to="/" className="flex items-center gap-2 font-semibold">
            <GraduationCap className="h-6 w-6 text-primary" />
            <span>Dialog</span>
            <span className="text-muted-foreground font-normal">
              Course Processor
            </span>
          </Link>
        </div>
      </header>

      <main className="container py-10">
        <Routes>
          <Route path="/" element={<UploadPage />} />
          <Route path="/jobs/:id" element={<JobPage />} />
        </Routes>
      </main>
    </div>
  );
}
