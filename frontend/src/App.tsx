import { Outlet } from "react-router";
import Navbar from "./components/navbar";
import Footer from "./components/footer";
import ScrollToTop from "./hooks/ScrollToTop";

function App() {
  return (
    <div className="min-h-screen flex flex-col">
      <ScrollToTop />
      <Navbar />
      <Outlet />
      <Footer />
    </div>
  );
}

export default App;
