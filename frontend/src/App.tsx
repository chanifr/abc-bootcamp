import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Layout } from './components/shared/Layout';
import { CandidatesPage } from './pages/CandidatesPage';
import { CandidateDetailPage } from './pages/CandidateDetailPage';
import { CandidateComparePage } from './pages/CandidateComparePage';
import { PositionsPage } from './pages/PositionsPage';
import { PositionDetailPage } from './pages/PositionDetailPage';
import { IngestionPage } from './pages/IngestionPage';

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<CandidatesPage />} />
          <Route path="/candidates/:id" element={<CandidateDetailPage />} />
          <Route path="/candidates/compare" element={<CandidateComparePage />} />
          <Route path="/positions" element={<PositionsPage />} />
          <Route path="/positions/:id" element={<PositionDetailPage />} />
          <Route path="/ingestion" element={<IngestionPage />} />
        </Routes>
      </Layout>
    </Router>
  );
}

export default App;
