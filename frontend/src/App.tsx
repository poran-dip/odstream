import { BrowserRouter, Route, Routes } from "react-router";
import ObjectDetectionPage from "./pages/ObjectDetection";
import RecordingsPage from "./pages/Recordings";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<ObjectDetectionPage />} />
        <Route
          path="/recordings"
          element={<RecordingsPage onBack={() => window.history.back()} />}
        />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
