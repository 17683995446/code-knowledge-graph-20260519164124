import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Home from './pages/Home';
import Graph from './pages/Graph';
import Chat from './pages/Chat';
import Search from './pages/Search';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Home />} />
          <Route path="graph/:projectId" element={<Graph />} />
          <Route path="chat/:projectId" element={<Chat />} />
          <Route path="search/:projectId" element={<Search />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
