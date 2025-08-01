import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { CssBaseline, Box, Typography, AppBar, Toolbar, Button } from '@mui/material';
import { Upload, Code, MessageCircle, Settings } from 'lucide-react';
import ProjectUpload from './components/ProjectUpload';
import ProjectList from './components/ProjectList';
import ChatInterface from './components/ChatInterface';
import CodeConverter from './components/CodeConverter';
import ProjectDetails from './components/ProjectDetails';

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
    background: {
      default: '#f5f5f5',
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
    h4: {
      fontWeight: 600,
    },
    h5: {
      fontWeight: 600,
    },
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
          <AppBar position="static" elevation={2}>
            <Toolbar>
              <Typography variant="h6" component="div" sx={{ flexGrow: 1, fontWeight: 'bold' }}>
                Code Modernization Tool
              </Typography>
              <Box sx={{ display: 'flex', gap: 1 }}>
                <Button color="inherit" startIcon={<Upload size={20} />} component={Link} to="/">
                  Upload
                </Button>
                <Button color="inherit" startIcon={<Code size={20} />} component={Link} to="/projects">
                  Projects
                </Button>
                <Button color="inherit" startIcon={<MessageCircle size={20} />} component={Link} to="/chat">
                  Chat
                </Button>
                <Button color="inherit" startIcon={<Settings size={20} />} component={Link} to="/convert">
                  Convert
                </Button>
              </Box>
            </Toolbar>
          </AppBar>
          <Box component="main" sx={{ flexGrow: 1, p: 3 }}>
            <Routes>
              <Route path="/" element={<ProjectUpload />} />
              <Route path="/projects" element={<ProjectList />} />
              <Route path="/projects/:projectId" element={<ProjectDetails />} />
              <Route path="/chat" element={<ChatInterface />} />
              <Route path="/convert" element={<CodeConverter />} />
            </Routes>
          </Box>
        </Box>
      </Router>
    </ThemeProvider>
  );
}

export default App; 