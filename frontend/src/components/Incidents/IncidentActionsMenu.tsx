import { useMutation, useQueryClient } from "@tanstack/react-query"
import { EllipsisVertical, ShieldCheck } from "lucide-react"
import { useState } from "react"

import type { IncidentPublic } from "@/client"
import { IncidentsService } from "@/client"
import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import useCustomToast from "@/hooks/useCustomToast"
import { handleError } from "@/utils"
import DeleteIncident from "./DeleteIncident"
import EditIncident from "./EditIncident"

interface IncidentActionsMenuProps {
  Incident: IncidentPublic
}

export const IncidentActionsMenu = ({ Incident }: IncidentActionsMenuProps) => {
  const [open, setOpen] = useState(false)
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()

  const resolveMutation = useMutation({
    mutationFn: () => IncidentsService.resolveIncident({ id: Incident.id }),
    onSuccess: () => {
      showSuccessToast("Incident resolved successfully")
      setOpen(false)
    },
    onError: handleError.bind(showErrorToast),
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ["Incidents"] })
    },
  })

  return (
    <DropdownMenu open={open} onOpenChange={setOpen}>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" size="icon">
          <EllipsisVertical />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        <EditIncident Incident={Incident} onSuccess={() => setOpen(false)} />
        {Incident.status !== "resolved" && (
          <DropdownMenuItem
            onClick={() => resolveMutation.mutate()}
            disabled={resolveMutation.isPending}
          >
            <ShieldCheck />
            Resolve Incident
          </DropdownMenuItem>
        )}
        <DeleteIncident id={Incident.id} onSuccess={() => setOpen(false)} />
      </DropdownMenuContent>
    </DropdownMenu>
  )
}
