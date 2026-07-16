import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { AlertCircle, CheckCircle2, Loader2 } from "lucide-react";

import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { cn } from "@/lib/utils";
import type { Job } from "@/types";

function useElapsed(startIso: string): string {
  const [now, setNow] = useState(() => Date.now());
  useEffect(() => {
    const t = setInterval(() => setNow(Date.now()), 1000);
    return () => clearInterval(t);
  }, []);
  const seconds = Math.max(0, Math.floor((now - new Date(startIso).getTime()) / 1000));
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return m > 0 ? `${m}m ${s}s` : `${s}s`;
}

const STEPS = ["queued", "processing", "completed"] as const;

export default function ProcessingView({ job }: { job: Job }) {
  const elapsed = useElapsed(job.created_at);

  if (job.status === "failed") {
    return (
      <div className="mx-auto max-w-2xl">
        <Card className="border-destructive/40">
          <CardHeader>
            <div className="flex items-center gap-2 text-destructive">
              <AlertCircle className="h-5 w-5" />
              <CardTitle className="text-xl">Processing Failed</CardTitle>
            </div>
            <CardDescription>{job.filename}</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="rounded-md bg-destructive/10 p-3 text-sm text-destructive">
              {job.error ?? "An unknown error occurred."}
            </p>
            <Button asChild variant="outline">
              <Link to="/">Try another file</Link>
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  const currentIndex = STEPS.indexOf(job.status as (typeof STEPS)[number]);

  return (
    <div className="mx-auto max-w-2xl">
      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <Loader2 className="h-5 w-5 animate-spin text-primary" />
            <CardTitle className="text-xl">Processing Module</CardTitle>
          </div>
          <CardDescription>
            {job.filename} · {elapsed} elapsed
          </CardDescription>
        </CardHeader>
        <CardContent>
          <ol className="space-y-4">
            {STEPS.slice(0, 2).map((step, i) => {
              const done = i < currentIndex;
              const active = i === currentIndex;
              return (
                <li key={step} className="flex items-center gap-3">
                  <span
                    className={cn(
                      "flex h-7 w-7 items-center justify-center rounded-full border text-xs",
                      done && "border-primary bg-primary text-primary-foreground",
                      active && "border-primary text-primary",
                      !done && !active && "border-border text-muted-foreground",
                    )}
                  >
                    {done ? (
                      <CheckCircle2 className="h-4 w-4" />
                    ) : active ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                      i + 1
                    )}
                  </span>
                  <span
                    className={cn(
                      "text-sm capitalize",
                      active ? "font-medium" : "text-muted-foreground",
                    )}
                  >
                    {step === "queued" ? "Queued for processing" : "Extracting & classifying"}
                  </span>
                </li>
              );
            })}
          </ol>
          <p className="mt-6 text-xs text-muted-foreground">
            This can take several minutes for a full course module. The page
            updates automatically.
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
