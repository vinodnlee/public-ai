import { useEffect, useMemo, useState } from 'react'
import {
  Alert,
  Box,
  Button,
  Checkbox,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  FormControlLabel,
  Stack,
  TextField,
  Typography,
} from '@mui/material'
import type { AgentConfig } from '../../api/agentConfigApi'

interface AgentConfigDialogProps {
  open: boolean
  config: AgentConfig | null
  sessionSelection?: { enabled_skills: string[]; skill_dirs: string[]; mcp_servers: string[] } | null
  isSaving?: boolean
  error?: string | null
  onClose: () => void
  onSave: (payload: { enabled_skills: string[]; skill_dirs: string[]; mcp_servers: string[] }) => void
  onApplyToSession?: (payload: {
    enabled_skills: string[]
    skill_dirs: string[]
    mcp_servers: string[]
  }) => void
}

function splitLines(text: string): string[] {
  return text
    .split('\n')
    .map((x) => x.trim())
    .filter(Boolean)
}

export function AgentConfigDialog({
  open,
  config,
  sessionSelection = null,
  isSaving = false,
  error = null,
  onClose,
  onSave,
  onApplyToSession,
}: AgentConfigDialogProps) {
  const [enabledSkills, setEnabledSkills] = useState<string[]>([])
  const [skillDirsText, setSkillDirsText] = useState('')
  const [mcpServersText, setMcpServersText] = useState('')

  useEffect(() => {
    if (sessionSelection) {
      setEnabledSkills(sessionSelection.enabled_skills ?? [])
      setSkillDirsText((sessionSelection.skill_dirs ?? []).join('\n'))
      setMcpServersText((sessionSelection.mcp_servers ?? []).join('\n'))
      return
    }
    if (!config) return
    setEnabledSkills(config.enabled_skills ?? [])
    setSkillDirsText((config.skill_dirs ?? []).join('\n'))
    setMcpServersText((config.mcp_servers ?? []).join('\n'))
  }, [config, sessionSelection])

  const payload = {
    enabled_skills: enabledSkills,
    skill_dirs: splitLines(skillDirsText),
    mcp_servers: splitLines(mcpServersText),
  }

  const available = useMemo(() => config?.available_skills ?? [], [config])

  const toggleSkill = (id: string, checked: boolean) => {
    setEnabledSkills((prev) =>
      checked ? Array.from(new Set([...prev, id])) : prev.filter((x) => x !== id)
    )
  }

  return (
    <Dialog open={open} onClose={onClose} fullWidth maxWidth="md">
      <DialogTitle>Agent Skills & MCP</DialogTitle>
      <DialogContent dividers>
        <Stack spacing={2}>
          {error && <Alert severity="error">{error}</Alert>}

          <Box>
            <Typography variant="subtitle2" sx={{ mb: 1 }}>
              Enabled Skills
            </Typography>
            {available.length === 0 ? (
              <Typography variant="body2" color="text.secondary">
                No registered skills found.
              </Typography>
            ) : (
              <Stack>
                {available.map((s) => (
                  <FormControlLabel
                    key={s.id}
                    control={
                      <Checkbox
                        checked={enabledSkills.includes(s.id)}
                        onChange={(_, checked) => toggleSkill(s.id, checked)}
                      />
                    }
                    label={`${s.name} (${s.id}) - ${s.target}`}
                  />
                ))}
              </Stack>
            )}
          </Box>

          <TextField
            label="Skill Directories (one per line)"
            multiline
            minRows={3}
            value={skillDirsText}
            onChange={(e) => setSkillDirsText(e.target.value)}
            fullWidth
          />

          <TextField
            label="MCP Servers (one per line)"
            multiline
            minRows={3}
            value={mcpServersText}
            onChange={(e) => setMcpServersText(e.target.value)}
            placeholder="http://localhost:9123/mcp"
            fullWidth
          />
        </Stack>
      </DialogContent>
      <DialogActions>
        {onApplyToSession && (
          <Button onClick={() => onApplyToSession(payload)} disabled={isSaving}>
            Apply To Current Chat
          </Button>
        )}
        <Button onClick={onClose} disabled={isSaving}>
          Cancel
        </Button>
        <Button
          variant="contained"
          onClick={() => onSave(payload)}
          disabled={isSaving}
        >
          Save
        </Button>
      </DialogActions>
    </Dialog>
  )
}
