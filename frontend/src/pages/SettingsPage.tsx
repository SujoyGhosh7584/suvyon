import { FormEvent, useState } from "react";
import { ThemePicker } from "@/components/ThemePicker";
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
      <div className="relative overflow-hidden rounded-[2rem] bg-ink-900 p-8 text-white shadow-panel">
        <p className="mb-2 text-xs font-semibold uppercase tracking-[0.22em] text-ink-300">
          Account
        </p>
        <h1 className="font-display text-4xl font-extrabold">Settings</h1>
        <p className="mt-2 text-ink-300">Appearance, profile, and account security.</p>
      </div>

      {message && (
        <div className="rounded-xl bg-emerald-50 px-3 py-2 text-sm text-emerald-700">
          {message}
        </div>
      )}
      {error && (
        <div className="rounded-xl bg-red-50 px-3 py-2 text-sm text-red-700">{error}</div>
      )}

      <div className="card space-y-3 p-6">
        <div>
          <div className="font-semibold">Appearance</div>
          <p className="mt-1 text-sm text-ink-500">
            Saved on this device only. Switching themes is a CSS change — nothing extra to host.
          </p>
        </div>
        <ThemePicker />
      </div>

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
