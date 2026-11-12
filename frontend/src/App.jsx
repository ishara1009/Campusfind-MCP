import { Route, Routes } from "react-router-dom";

import Navbar from "./components/Navbar";
import FindItemPage from "./pages/FindItemPage";
import ReportItemPage from "./pages/ReportItemPage";
import ReportStatusPage from "./pages/ReportStatusPage";


export default function App() {
  return (
    <div className="app-shell">
      <Navbar />
      <main>
        <Routes>
          <Route path="/" element={<FindItemPage />} />
          <Route path="/report" element={<ReportItemPage />} />
          <Route path="/status" element={<ReportStatusPage />} />
        </Routes>
      </main>
      <footer>CampusFind · A local MCP-powered portfolio project</footer>
    </div>
  );
}
