import { EllipsisVertical } from "lucide-react"
import { useState } from "react"

import type { ProjectPublic } from "@/client"
import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import DeleteProject from "../Projects/DeleteProject"
import EditProject from "../Projects/EditProject"

interface ProjectActionsMenuProps {
  Project: ProjectPublic
}

export const ProjectActionsMenu = ({ Project }: ProjectActionsMenuProps) => {
  const [open, setOpen] = useState(false)

  return (
    <DropdownMenu open={open} onOpenChange={setOpen}>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" size="icon">
          <EllipsisVertical />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        <EditProject Project={Project} onSuccess={() => setOpen(false)} />
        <DeleteProject id={Project.id} onSuccess={() => setOpen(false)} />
      </DropdownMenuContent>
    </DropdownMenu>
  )
}

