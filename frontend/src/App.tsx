import { StrictMode } from 'react'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import './index.css'
import { Layout } from './components/layout'
import DashboardPage from './pages/dashboard'
import ProjectsPage from './pages/projects'
import ProjectDetailPage from './pages/projects/[id]'
import TasksPage from './pages/tasks'
import CostsPage from './pages/costs'

function App() {
  return (
    <StrictMode>
      <BrowserRouter>
        <Layout>
          <Routes>
            <Route path="/dev/" element={<DashboardPage />} />
            <Route path="/dev/projects" element={<ProjectsPage />} />
            <Route path="/dev/projects/:id" element={<ProjectDetailPage />} />
            <Route path="/dev/tasks" element={<TasksPage />} />
            <Route path="/dev/costs" element={<CostsPage />} />
          </Routes>
        </Layout>
      </BrowserRouter>
    </StrictMode>
  )
}

export default App
