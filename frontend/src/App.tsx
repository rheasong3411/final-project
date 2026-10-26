import { Link, Route, Routes } from "react-router-dom";
import { EmptyState } from "./components/Common";
import { Layout } from "./components/Layout";
import { About } from "./pages/About";
import { Compare } from "./pages/Compare";
import { Explore } from "./pages/Explore";
import { FindMyFit } from "./pages/FindMyFit";
import { Home } from "./pages/Home";
import { OpportunityDetail } from "./pages/OpportunityDetail";

function NotFound() {
  return (
    <div className="container section">
      <EmptyState title="This page doesn't exist">
        <p className="muted">The link may be mistyped.</p>
        <Link className="btn btn-primary" to="/">Go to the home page</Link>
      </EmptyState>
    </div>
  );
}

export default function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/explore" element={<Explore />} />
        <Route path="/opportunities/:id" element={<OpportunityDetail />} />
        <Route path="/compare" element={<Compare />} />
        <Route path="/find-my-fit" element={<FindMyFit />} />
        <Route path="/about" element={<About />} />
        <Route path="*" element={<NotFound />} />
      </Routes>
    </Layout>
  );
}
