import { FormEvent, useState } from "react";
import { useAuth } from "@/context/AuthContext";
import { getErrorMessage } from "@/lib/api";
import { authApi, usersApi } from "@/lib/services";

export function SettingsPage() {
  const { user, refreshUser } = useAuth();
  const [fullName, setFullName] = useState(user?.full_name || "");
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);

  async function saveProfile(e: FormEvent) {
    e.preventDefault();
    setSaving(true);
    setError("");
    setMessage("");
    try {
      await usersApi.updateMe({ full_name: fullName });
      await refreshUser();
      setMessage("Profile updated.");
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setSaving(false);
    }
  }

  async function changePassword(e: FormEvent) {
    e.preventDefault();
    setSaving(true);
    setError("");
    setMessage("");
    try {
      await authApi.changePassword(currentPassword, newPassword);
      setCurrentPassword("");
      setNewPassword("");
      setMessage("Password changed.");
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="mx-auto max-w-2xl space-y-8">
      <div className="rounded-3xl border border-slate-200 bg-gradient-to-r from-slate-50 to-white p-6">
        <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-600">
          Account
        </p>
        <h1 className="font-display text-3xl font-extrabold">Settings</h1>
        <p className="mt-2 text-ink-600">Manage your profile and account security.</p>
      </div>

      {message && (
        <div className="rounded-xl bg-emerald-50 px-3 py-2 text-sm text-emerald-700">
          {message}
        </div>
      )}
      {error && (
        <div className="rounded-xl bg-red-50 px-3 py-2 text-sm text-red-700">{error}</div>
      )}

      <form className="card space-y-4 p-6" onSubmit={saveProfile}>
        <div className="font-semibold">Profile</div>
        <div>
          <label className="label">Email</label>
          <input className="input" value={user?.email || ""} disabled />
        </div>
        <div>
          <label className="label">Full name</label>
          <input
            className="input"
            value={fullName}
            onChange={(e) => setFullName(e.target.value)}
            required
            minLength={2}
          />
        </div>
        <button className="btn-primary" disabled={saving}>
          Save profile
        </button>
      </form>

      <form className="card space-y-4 p-6" onSubmit={changePassword}>
        <div className="font-semibold">Change password</div>
        <div>
          <label className="label">Current password</label>
          <input
            className="input"
            type="password"
            required
            minLength={8}
            value={currentPassword}
            onChange={(e) => setCurrentPassword(e.target.value)}
          />
        </div>
        <div>
          <label className="label">New password</label>
          <input
            className="input"
            type="password"
            required
            minLength={8}
            value={newPassword}
            onChange={(e) => setNewPassword(e.target.value)}
          />
        </div>
        <button className="btn-outline" disabled={saving}>
          Update password
        </button>
      </form>
    </div>
  );
}
