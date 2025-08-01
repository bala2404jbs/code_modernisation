import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  TextField,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
  CircularProgress,
  Paper,
  List,
  ListItem,
  ListItemText,
  Divider,
} from '@mui/material';
import { Send, MessageCircle } from 'lucide-react';
import axios from 'axios';

interface ChatMessage {
  question: string;
  answer: string;
  timestamp: string;
}

const ChatInterface: React.FC = () => {
  const [projects, setProjects] = useState<any[]>([]);
  const [selectedProject, setSelectedProject] = useState('');
  const [question, setQuestion] = useState('');
  const [chatHistory, setChatHistory] = useState<ChatMessage[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchProjects();
  }, []);

  const fetchProjects = async () => {
    try {
      const response = await axios.get('/api/projects');
      setProjects(response.data.filter((p: any) => p.status === 'parsed'));
    } catch (error) {
      console.error('Failed to fetch projects:', error);
    }
  };

  const handleSendMessage = async () => {
    if (!selectedProject || !question.trim()) {
      setError('Please select a project and enter a question');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const response = await axios.post('/api/chat', {
        project_id: selectedProject,
        question: question.trim(),
      });

      const newMessage: ChatMessage = {
        question: question.trim(),
        answer: response.data.answer,
        timestamp: new Date().toLocaleString(),
      };

      setChatHistory(prev => [newMessage, ...prev]);
      setQuestion('');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to send message');
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (event: React.KeyboardEvent) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      handleSendMessage();
    }
  };

  const selectedProjectData = projects.find(p => p.project_id === selectedProject);

  return (
    <Box sx={{ maxWidth: 1000, mx: 'auto' }}>
      <Typography variant="h4" gutterBottom>
        Chat with Codebase
      </Typography>

      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Select Project
          </Typography>
          
          <FormControl fullWidth sx={{ mb: 2 }}>
            <InputLabel>Choose a Project</InputLabel>
            <Select
              value={selectedProject}
              label="Choose a Project"
              onChange={(e) => setSelectedProject(e.target.value)}
            >
              {projects.map((project) => (
                <MenuItem key={project.project_id} value={project.project_id}>
                  {project.project_name} ({project.source_language})
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          {selectedProjectData && (
            <Alert severity="info" sx={{ mb: 2 }}>
              Chatting about: {selectedProjectData.project_name} ({selectedProjectData.source_language})
            </Alert>
          )}
        </CardContent>
      </Card>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <Box sx={{ display: 'flex', gap: 2, mb: 3 }}>
        <TextField
          fullWidth
          multiline
          rows={3}
          label="Ask a question about your codebase"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyPress={handleKeyPress}
          disabled={!selectedProject || loading}
          placeholder="e.g., What are the main functions in this project? How is authentication handled?"
        />
        <Button
          variant="contained"
          onClick={handleSendMessage}
          disabled={!selectedProject || !question.trim() || loading}
          startIcon={loading ? <CircularProgress size={20} /> : <Send />}
          sx={{ minWidth: 120, alignSelf: 'flex-end' }}
        >
          {loading ? 'Sending...' : 'Send'}
        </Button>
      </Box>

      {chatHistory.length > 0 && (
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Chat History
            </Typography>
            
            <List>
              {chatHistory.map((message, index) => (
                <React.Fragment key={index}>
                  <ListItem alignItems="flex-start">
                    <ListItemText
                      primary={
                        <Box>
                          <Typography variant="subtitle2" color="primary" gutterBottom>
                            Question ({message.timestamp})
                          </Typography>
                          <Typography variant="body1" sx={{ mb: 2 }}>
                            {message.question}
                          </Typography>
                          <Typography variant="subtitle2" color="secondary" gutterBottom>
                            Answer
                          </Typography>
                          <Paper sx={{ p: 2, backgroundColor: '#f5f5f5' }}>
                            <Typography variant="body1" component="pre" sx={{ 
                              whiteSpace: 'pre-wrap', 
                              fontFamily: 'inherit',
                              margin: 0 
                            }}>
                              {message.answer}
                            </Typography>
                          </Paper>
                        </Box>
                      }
                    />
                  </ListItem>
                  {index < chatHistory.length - 1 && <Divider />}
                </React.Fragment>
              ))}
            </List>
          </CardContent>
        </Card>
      )}

      {chatHistory.length === 0 && selectedProject && (
        <Card>
          <CardContent>
            <Box sx={{ textAlign: 'center', py: 4 }}>
              <MessageCircle size={48} color="#ccc" />
              <Typography variant="h6" color="text.secondary" sx={{ mt: 2 }}>
                Start a conversation about your codebase
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Ask questions about functions, classes, architecture, or any aspect of your code
              </Typography>
            </Box>
          </CardContent>
        </Card>
      )}
    </Box>
  );
};

export default ChatInterface; 