import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Grid,
  Chip,
  CircularProgress,
  FormControlLabel,
  Switch,
} from '@mui/material';
import { Code, Eye } from 'lucide-react';
import axios from 'axios';

const ProjectList: React.FC = () => {
  const [projects, setProjects] = useState<any[]>([]);
  const [allProjects, setAllProjects] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [showOnlyParsed, setShowOnlyParsed] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    fetchProjects();
  }, []);

  useEffect(() => {
    // Filter projects based on the switch
    if (showOnlyParsed) {
      setProjects(allProjects.filter(project => project.status === 'parsed'));
    } else {
      setProjects(allProjects);
    }
  }, [allProjects, showOnlyParsed]);

  const fetchProjects = async () => {
    try {
      console.log('Fetching projects...');
      const response = await axios.get('/api/projects');
      console.log('Projects response:', response.data);
      setAllProjects(response.data);
    } catch (error) {
      console.error('Failed to fetch projects:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" gutterBottom>
          Projects
        </Typography>
        <FormControlLabel
          control={
            <Switch
              checked={showOnlyParsed}
              onChange={(e) => setShowOnlyParsed(e.target.checked)}
            />
          }
          label="Show only parsed projects"
        />
      </Box>
      
      <Grid container spacing={3}>
        {projects.map((project) => (
          <Grid item xs={12} sm={6} md={4} key={project.project_id}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                  <Code size={20} />
                  <Typography variant="h6">{project.project_name}</Typography>
                </Box>
                
                <Chip 
                  label={project.status} 
                  color={project.status === 'parsed' ? 'success' : 'warning'}
                  size="small"
                  sx={{ mb: 2 }}
                />
                
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  {project.message}
                </Typography>
                
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Language: {project.source_language}
                  {project.source_framework && ` • Framework: ${project.source_framework}`}
                </Typography>
                
                <Button
                  variant="outlined"
                  size="small"
                  startIcon={<Eye />}
                  onClick={() => navigate(`/projects/${project.project_id}`)}
                >
                  View Details
                </Button>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
      
      {projects.length === 0 && (
        <Box sx={{ textAlign: 'center', p: 4 }}>
          <Typography variant="h6" color="text.secondary">
            {showOnlyParsed 
              ? "No parsed projects found. Upload and parse a project to get started."
              : "No projects found. Upload a project to get started."
            }
          </Typography>
        </Box>
      )}
    </Box>
  );
};

export default ProjectList; 