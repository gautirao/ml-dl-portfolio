import { BrowserRouter, Routes, Route } from "react-router-dom";
import Layout from "./components/Layout";
import UploadPage from "./pages/UploadPage";
import TransactionsPage from "./pages/TransactionsPage";
import AnalyticsPage from "./pages/AnalyticsPage";
import ChatPage from "./pages/ChatPage";

function App() {
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/" element={<UploadPage />} />
          <Route path="/transactions" element={<TransactionsPage />} />
          <Route path="/analytics" element={<AnalyticsPage />} />
          <Route path="/chat" element={<ChatPage />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  );
}

export default App;
