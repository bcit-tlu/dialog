import { useParams } from "react-router-dom";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

// Placeholder — the processing/results views are built in Step 7.
// This exists so the /jobs/:id route resolves after an upload.
export default function JobPage() {
  const { id } = useParams<{ id: string }>();

  return (
    <div className="mx-auto max-w-2xl">
      <Card>
        <CardHeader>
          <CardTitle>Job Created</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2">
          <p className="text-sm text-muted-foreground">
            Job ID: <code className="text-foreground">{id}</code>
          </p>
          <p className="text-sm text-muted-foreground">
            Processing and results views arrive in the next step.
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
