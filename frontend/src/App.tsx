import { Navigate, Route, Routes } from "react-router-dom";
import { Adaptive } from "@/components/Adaptive";
import { ProtectedRoute } from "@/components/ProtectedRoute";
import { AppShell } from "@/layouts/AppShell";
import { MobileShell } from "@/layouts/MobileShell";
import { AgentsPage } from "@/pages/AgentsPage";
import { ChatPage } from "@/pages/ChatPage";
import { KnowledgePage } from "@/pages/KnowledgePage";
import { ForgotPasswordPage } from "@/pages/ForgotPasswordPage";
import { LandingPage } from "@/pages/LandingPage";
import { LoginPage } from "@/pages/LoginPage";
import { OverviewPage } from "@/pages/OverviewPage";
import { RegisterPage } from "@/pages/RegisterPage";
import { SettingsPage } from "@/pages/SettingsPage";
import { VerifyEmailPage } from "@/pages/VerifyEmailPage";
import { WorkspacesPage } from "@/pages/WorkspacesPage";
import { MobileAgentsPage } from "@/pages/mobile/MobileAgentsPage";
import { MobileChatPage } from "@/pages/mobile/MobileChatPage";
import { MobileLandingPage } from "@/pages/mobile/MobileLandingPage";
import { MobileWorkspacesPage } from "@/pages/mobile/MobileWorkspacesPage";

function WorkspaceLayout() {
  return <Adaptive mobile={MobileShell} desktop={AppShell} />;
}

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Adaptive mobile={MobileLandingPage} desktop={LandingPage} />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route path="/verify-email" element={<VerifyEmailPage />} />
      <Route path="/forgot-password" element={<ForgotPasswordPage />} />

      <Route element={<ProtectedRoute />}>
        <Route
          path="/app"
          element={<Adaptive mobile={MobileWorkspacesPage} desktop={WorkspacesPage} />}
        />
        <Route path="/app/w/:workspaceId" element={<WorkspaceLayout />}>
          <Route index element={<Navigate to="overview" replace />} />
          <Route path="overview" element={<OverviewPage />} />
          <Route path="chat" element={<Adaptive mobile={MobileChatPage} desktop={ChatPage} />} />
          <Route
            path="chat/:conversationId"
            element={<Adaptive mobile={MobileChatPage} desktop={ChatPage} />}
          />
          <Route
            path="agents"
            element={<Adaptive mobile={MobileAgentsPage} desktop={AgentsPage} />}
          />
          <Route
            path="agents/:agentId"
            element={<Adaptive mobile={MobileAgentsPage} desktop={AgentsPage} />}
          />
          <Route path="knowledge" element={<KnowledgePage />} />
          <Route path="settings" element={<SettingsPage />} />
        </Route>
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
