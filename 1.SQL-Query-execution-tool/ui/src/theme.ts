import { createTheme } from '@mui/material/styles'

export const theme = createTheme({
    palette: {
        mode: 'light',
        primary: {
            main: '#6366f1',   // indigo-500
            light: '#818cf8',
            dark: '#4f46e5',
            contrastText: '#ffffff',
        },
        secondary: {
            main: '#0ea5e9',   // sky-500
            contrastText: '#ffffff',
        },
        background: {
            default: '#f1f5f9',  // slate-100
            paper: '#ffffff',
        },
        text: {
            primary: '#0f172a',   // slate-900
            secondary: '#64748b', // slate-500
        },
        divider: '#e2e8f0',     // slate-200
        error: { main: '#ef4444' },
        success: { main: '#22c55e' },
    },
    typography: {
        fontFamily: '"Inter", "Roboto", "Helvetica Neue", Arial, sans-serif',
        h6: { fontWeight: 600, letterSpacing: '-0.01em' },
        subtitle2: { fontWeight: 600 },
        body1: { lineHeight: 1.65 },
        body2: { lineHeight: 1.6 },
    },
    shape: { borderRadius: 10 },
    components: {
        MuiCssBaseline: {
            styleOverrides: {
                body: {
                    margin: 0,
                    padding: 0,
                    WebkitFontSmoothing: 'antialiased',
                    MozOsxFontSmoothing: 'grayscale',
                },
            },
        },
        MuiButton: {
            styleOverrides: {
                root: { textTransform: 'none', fontWeight: 500, borderRadius: 8 },
            },
        },
        MuiIconButton: {
            styleOverrides: {
                root: { borderRadius: 8 },
            },
        },
        MuiDrawer: {
            styleOverrides: {
                paper: { borderRadius: 0 },
            },
        },
        MuiTooltip: {
            styleOverrides: {
                tooltip: { fontSize: '0.75rem' },
            },
        },
        MuiChip: {
            styleOverrides: {
                root: { fontWeight: 500 },
            },
        },
    },
})
