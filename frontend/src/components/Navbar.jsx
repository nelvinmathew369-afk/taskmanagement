import React from "react";
import { CheckSquare, LogOut, User as UserIcon } from "lucide-react";

export default function Navbar({ user, onLogout }) {
  return (
    <header className="navbar">
      <div className="brand">
        <div className="brand-icon">
          <CheckSquare size={22} />
        </div>
        <div>
          <h1 className="brand-title">TaskFlow AI</h1>
          <div className="brand-subtitle">FastAPI • MySQL • LLM Assistant</div>
        </div>
      </div>

      <div className="user-nav">
        {user && (
          <div className="user-badge">
            <UserIcon size={16} />
            <span>{user.full_name || user.username}</span>
          </div>
        )}
        <button className="btn-logout" onClick={onLogout} title="Sign Out">
          <LogOut size={16} />
          <span>Sign Out</span>
        </button>
      </div>
    </header>
  );
}
