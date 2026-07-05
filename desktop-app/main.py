"""
Power Trading Desktop Application
Professional cross-platform desktop app using CustomTkinter
Connects to Railway-deployed backend API
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import requests
import json
import threading
import os
import sys
from datetime import datetime, timedelta
from PIL import Image, ImageTk
import io
import base64
import matplotlib
matplotlib.use("Agg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.dates as mdates
import pandas as pd

# Configure appearance
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Configuration
API_BASE_URL = "https://power-trading-application-production.up.railway.app/api"

class PowerTradingDesktopApp:
    """Main desktop application for Power Trading Analytics"""
    
    def __init__(self):
        self.window = ctk.CTk()
        self.window.title("Power Trading Analytics - Desktop")
        self.window.geometry("1400x900")
        self.window.minsize(1200, 700)
        
        # Set icon if available
        try:
            self.window.iconbitmap(default="")
        except:
            pass
        
        # State
        self.clients = []
        self.current_client = None
        self.transactions = []
        self.energy_schedule_days = []
        
        # Build UI
        self._build_ui()
        
        # Load initial data
        self._load_clients()
        
    def _build_ui(self):
        """Build the user interface"""
        # Main container
        self.main_container = ctk.CTkFrame(self.window, fg_color="#1a1a2e")
        self.main_container.pack(fill="both", expand=True, padx=0, pady=0)
        
        # ================ HEADER ================
        self.header = ctk.CTkFrame(self.main_container, height=60, fg_color="#16213e", corner_radius=0)
        self.header.pack(fill="x", padx=0, pady=0)
        self.header.pack_propagate(False)
        
        ctk.CTkLabel(
            self.header, 
            text="POWER TRADING ANALYTICS", 
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#4fc3f7"
        ).pack(side="left", padx=20, pady=10)
        
        # Status indicator
        self.status_frame = ctk.CTkFrame(self.header, fg_color="transparent")
        self.status_frame.pack(side="right", padx=20, pady=10)
        
        self.status_dot = ctk.CTkLabel(self.status_frame, text="  ", width=10, height=10, corner_radius=5, fg_color="#ff5252")
        self.status_dot.pack(side="left", padx=(0, 5))
        
        self.status_label = ctk.CTkLabel(self.status_frame, text="Checking connection...", font=ctk.CTkFont(size=11))
        self.status_label.pack(side="left")
        
        # Refresh button
        self.refresh_btn = ctk.CTkButton(
            self.status_frame, text="Refresh", width=80, height=28,
            command=self._refresh_data, font=ctk.CTkFont(size=11)
        )
        self.refresh_btn.pack(side="left", padx=(10, 0))
        
        # ================ MAIN CONTENT ================
        self.content = ctk.CTkFrame(self.main_container, fg_color="#1a1a2e")
        self.content.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Left sidebar
        self.sidebar = ctk.CTkFrame(self.content, width=250, fg_color="#16213e", corner_radius=10)
        self.sidebar.pack(side="left", fill="y", padx=(0, 10))
        self.sidebar.pack_propagate(False)
        
        ctk.CTkLabel(
            self.sidebar, 
            text="CLIENTS", 
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#4fc3f7"
        ).pack(padx=15, pady=(15, 5), anchor="w")
        
        # Client list
        self.client_list_frame = ctk.CTkScrollableFrame(self.sidebar, fg_color="transparent", height=300)
        self.client_list_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Upload button
        self.upload_btn = ctk.CTkButton(
            self.sidebar, text="Upload Excel File", 
            command=self._upload_file, height=40,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#0d47a1", hover_color="#1565c0"
        )
        self.upload_btn.pack(padx=15, pady=(5, 10), fill="x")
        
        # Quick actions
        ctk.CTkLabel(
            self.sidebar, 
            text="QUICK ACTIONS", 
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#4fc3f7"
        ).pack(padx=15, pady=(5, 5), anchor="w")
        
        actions = [
            ("Generate Report", self._generate_report),
            ("View All Transactions", self._view_all_transactions),
            ("Energy Schedule", self._view_energy_schedule),
        ]
        for text, cmd in actions:
            ctk.CTkButton(
                self.sidebar, text=text, command=cmd, height=32,
                font=ctk.CTkFont(size=12), fg_color="#1a237e", hover_color="#283593"
            ).pack(padx=15, pady=3, fill="x")
        
        # Right content area
        self.right_area = ctk.CTkFrame(self.content, fg_color="#16213e", corner_radius=10)
        self.right_area.pack(side="right", fill="both", expand=True)
        
        # Tab view
        self.tab_view = ctk.CTkTabview(self.right_area, fg_color="#1a1a2e")
        self.tab_view.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Dashboard tab
        self.dashboard_tab = self.tab_view.add("Dashboard")
        self._build_dashboard()
        
        # Transactions tab
        self.transactions_tab = self.tab_view.add("Transactions")
        self._build_transactions_tab()
        
        # Analytics tab
        self.analytics_tab = self.tab_view.add("Analytics")
        self._build_analytics_tab()
        
        # Settings tab
        self.settings_tab = self.tab_view.add("Settings")
        self._build_settings_tab()
        
        # Check connection
        self._check_connection()
        
    def _build_dashboard(self):
        """Build dashboard tab"""
        # Summary cards row
        cards_frame = ctk.CTkFrame(self.dashboard_tab, fg_color="transparent")
        cards_frame.pack(fill="x", padx=10, pady=(10, 5))
        
        self.metric_frames = {}
        metrics = [
            ("Total Clients", "clients", "#0d47a1"),
            ("Transactions", "transactions", "#00695c"),
            ("Files Uploaded", "files", "#e65100"),
            ("Schedule Days", "schedule", "#4a148c"),
        ]
        
        for i, (label, key, color) in enumerate(metrics):
            frame = ctk.CTkFrame(cards_frame, fg_color=color, corner_radius=8, height=80)
            frame.pack(side="left", fill="x", expand=True, padx=(0 if i == 0 else 5, 5 if i < len(metrics)-1 else 0), pady=5)
            frame.pack_propagate(False)
            
            ctk.CTkLabel(frame, text=label, font=ctk.CTkFont(size=11), text_color="white").pack(padx=10, pady=(10, 0), anchor="w")
            value_label = ctk.CTkLabel(frame, text="--", font=ctk.CTkFont(size=28, weight="bold"), text_color="white")
            value_label.pack(padx=10, pady=(0, 5), anchor="w")
            self.metric_frames[key] = value_label
        
        # Charts row
        charts_row = ctk.CTkFrame(self.dashboard_tab, fg_color="transparent")
        charts_row.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Chart 1: Transactions over time
        chart1_frame = ctk.CTkFrame(charts_row, fg_color="#0d1b2a", corner_radius=8)
        chart1_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))
        ctk.CTkLabel(chart1_frame, text="Transactions Over Time", font=ctk.CTkFont(size=12, weight="bold"), text_color="#4fc3f7").pack(padx=10, pady=(10, 0), anchor="w")
        
        self.fig1 = Figure(figsize=(5, 3), dpi=80, facecolor="#0d1b2a")
        self.ax1 = self.fig1.add_subplot(111)
        self.ax1.set_facecolor("#0d1b2a")
        self.ax1.tick_params(colors="white")
        self.ax1.spines["bottom"].set_color("#444")
        self.ax1.spines["left"].set_color("#444")
        self.canvas1 = FigureCanvasTkAgg(self.fig1, master=chart1_frame)
        self.canvas1.get_tk_widget().pack(fill="both", expand=True, padx=5, pady=5)
        
        # Chart 2: Portfolio comparison
        chart2_frame = ctk.CTkFrame(charts_row, fg_color="#0d1b2a", corner_radius=8)
        chart2_frame.pack(side="right", fill="both", expand=True, padx=(5, 0))
        ctk.CTkLabel(chart2_frame, text="Portfolio Comparison", font=ctk.CTkFont(size=12, weight="bold"), text_color="#4fc3f7").pack(padx=10, pady=(10, 0), anchor="w")
        
        self.fig2 = Figure(figsize=(5, 3), dpi=80, facecolor="#0d1b2a")
        self.ax2 = self.fig2.add_subplot(111)
        self.ax2.set_facecolor("#0d1b2a")
        self.ax2.tick_params(colors="white")
        self.ax2.spines["bottom"].set_color("#444")
        self.ax2.spines["left"].set_color("#444")
        self.canvas2 = FigureCanvasTkAgg(self.fig2, master=chart2_frame)
        self.canvas2.get_tk_widget().pack(fill="both", expand=True, padx=5, pady=5)
        
        # Recent activity
        activity_frame = ctk.CTkFrame(self.dashboard_tab, fg_color="#0d1b2a", corner_radius=8, height=150)
        activity_frame.pack(fill="x", padx=10, pady=(0, 10))
        activity_frame.pack_propagate(False)
        ctk.CTkLabel(activity_frame, text="Recent Activity", font=ctk.CTkFont(size=12, weight="bold"), text_color="#4fc3f7").pack(padx=10, pady=(10, 0), anchor="w")
        
        self.activity_text = ctk.CTkTextbox(activity_frame, height=80, fg_color="transparent", text_color="white", font=ctk.CTkFont(size=11))
        self.activity_text.pack(fill="both", expand=True, padx=10, pady=5)
        self.activity_text.insert("1.0", "No recent activity.\nClick Refresh to load data.")
        self.activity_text.configure(state="disabled")
        
    def _build_transactions_tab(self):
        """Build transactions tab"""
        # Filter bar
        filter_frame = ctk.CTkFrame(self.transactions_tab, fg_color="transparent")
        filter_frame.pack(fill="x", padx=10, pady=(10, 5))
        
        ctk.CTkLabel(filter_frame, text="Filter:", font=ctk.CTkFont(size=12)).pack(side="left", padx=(0, 5))
        
        self.filter_type = ctk.CTkOptionMenu(
            filter_frame, values=["All", "Buy", "Sell", "Scheduling"],
            width=120, font=ctk.CTkFont(size=11)
        )
        self.filter_type.pack(side="left", padx=5)
        self.filter_type.set("All")
        
        self.filter_report = ctk.CTkOptionMenu(
            filter_frame, values=["All", "GDAM", "DAM", "RTM", "SCH"],
            width=120, font=ctk.CTkFont(size=11)
        )
        self.filter_report.pack(side="left", padx=5)
        self.filter_report.set("All")
        
        ctk.CTkButton(
            filter_frame, text="Apply", width=70, height=28,
            command=self._apply_filters, font=ctk.CTkFont(size=11)
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            filter_frame, text="Export CSV", width=90, height=28,
            command=self._export_csv, font=ctk.CTkFont(size=11), fg_color="#00695c"
        ).pack(side="right", padx=5)
        
        # Table
        table_frame = ctk.CTkFrame(self.transactions_tab, fg_color="#0d1b2a", corner_radius=8)
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Treeview with scrollbar
        columns = ("Date", "Type", "Market", "Quantity (MW)", "Rate (Rs/MWh)", "Amount (Rs)")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=20)
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120, anchor="center")
        
        self.tree.column("Date", width=100)
        self.tree.column("Quantity (MW)", width=110)
        self.tree.column("Rate (Rs/MWh)", width=110)
        self.tree.column("Amount (Rs)", width=110)
        
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        scrollbar.pack(side="right", fill="y", pady=5)
        
        # Style the tree
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#0d1b2a", foreground="white", fieldbackground="#0d1b2a", rowheight=25)
        style.configure("Treeview.Heading", background="#16213e", foreground="white", font=("Arial", 10, "bold"))
        style.map("Treeview", background=[("selected", "#4fc3f7")])
        
    def _build_analytics_tab(self):
        """Build analytics tab"""
        # Summary stats row
        stats_frame = ctk.CTkFrame(self.analytics_tab, fg_color="transparent")
        stats_frame.pack(fill="x", padx=10, pady=(10, 5))
        
        self.analytics_labels = {}
        stats = [
            ("Total Buy Volume", "buy_vol", "0 MWh"),
            ("Total Sell Volume", "sell_vol", "0 MWh"),
            ("Net Amount", "net_amt", "Rs 0"),
            ("Avg Rate", "avg_rate", "Rs 0/MWh"),
        ]
        
        for i, (label, key, default) in enumerate(stats):
            frame = ctk.CTkFrame(stats_frame, fg_color="#0d1b2a", corner_radius=6, height=60)
            frame.pack(side="left", fill="x", expand=True, padx=(0 if i == 0 else 5, 5 if i < len(stats)-1 else 0))
            frame.pack_propagate(False)
            
            ctk.CTkLabel(frame, text=label, font=ctk.CTkFont(size=10), text_color="#888").pack(padx=10, pady=(8, 0), anchor="w")
            val = ctk.CTkLabel(frame, text=default, font=ctk.CTkFont(size=16, weight="bold"), text_color="#4fc3f7")
            val.pack(padx=10, pady=(0, 5), anchor="w")
            self.analytics_labels[key] = val
        
        # Charts for analytics
        charts_frame = ctk.CTkFrame(self.analytics_tab, fg_color="transparent")
        charts_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Chart 1: Hourly distribution
        chart_a = ctk.CTkFrame(charts_frame, fg_color="#0d1b2a", corner_radius=8)
        chart_a.pack(side="left", fill="both", expand=True, padx=(0, 5))
        ctk.CTkLabel(chart_a, text="Hourly Distribution", font=ctk.CTkFont(size=12, weight="bold"), text_color="#4fc3f7").pack(padx=10, pady=(10, 0), anchor="w")
        
        self.fig3 = Figure(figsize=(5, 3), dpi=80, facecolor="#0d1b2a")
        self.ax3 = self.fig3.add_subplot(111)
        self.ax3.set_facecolor("#0d1b2a")
        self.ax3.tick_params(colors="white")
        self.ax3.spines["bottom"].set_color("#444")
        self.ax3.spines["left"].set_color("#444")
        self.canvas3 = FigureCanvasTkAgg(self.fig3, master=chart_a)
        self.canvas3.get_tk_widget().pack(fill="both", expand=True, padx=5, pady=5)
        
        # Chart 2: Market breakdown
        chart_b = ctk.CTkFrame(charts_frame, fg_color="#0d1b2a", corner_radius=8)
        chart_b.pack(side="right", fill="both", expand=True, padx=(5, 0))
        ctk.CTkLabel(chart_b, text="Market Breakdown", font=ctk.CTkFont(size=12, weight="bold"), text_color="#4fc3f7").pack(padx=10, pady=(10, 0), anchor="w")
        
        self.fig4 = Figure(figsize=(5, 3), dpi=80, facecolor="#0d1b2a")
        self.ax4 = self.fig4.add_subplot(111)
        self.ax4.set_facecolor("#0d1b2a")
        self.ax4.tick_params(colors="white")
        self.ax4.spines["bottom"].set_color("#444")
        self.ax4.spines["left"].set_color("#444")
        self.canvas4 = FigureCanvasTkAgg(self.fig4, master=chart_b)
        self.canvas4.get_tk_widget().pack(fill="both", expand=True, padx=5, pady=5)
        
    def _build_settings_tab(self):
        """Build settings tab"""
        settings_container = ctk.CTkScrollableFrame(self.settings_tab, fg_color="transparent")
        settings_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # API Configuration
        ctk.CTkLabel(
            settings_container, text="API Configuration",
            font=ctk.CTkFont(size=16, weight="bold"), text_color="#4fc3f7"
        ).pack(padx=10, pady=(10, 5), anchor="w")
        
        api_frame = ctk.CTkFrame(settings_container, fg_color="#0d1b2a", corner_radius=8)
        api_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(api_frame, text="Backend URL:", font=ctk.CTkFont(size=12)).pack(padx=15, pady=(10, 5), anchor="w")
        
        self.api_url_entry = ctk.CTkEntry(api_frame, width=500, font=ctk.CTkFont(size=11))
        self.api_url_entry.pack(padx=15, pady=(0, 5), anchor="w")
        self.api_url_entry.insert(0, API_BASE_URL)
        
        ctk.CTkButton(
            api_frame, text="Test Connection", command=self._test_connection,
            width=120, height=30, font=ctk.CTkFont(size=11)
        ).pack(padx=15, pady=(0, 10), anchor="w")
        
        # Database actions
        ctk.CTkLabel(
            settings_container, text="Database Management",
            font=ctk.CTkFont(size=16, weight="bold"), text_color="#4fc3f7"
        ).pack(padx=10, pady=(15, 5), anchor="w")
        
        db_frame = ctk.CTkFrame(settings_container, fg_color="#0d1b2a", corner_radius=8)
        db_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkButton(
            db_frame, text="Reset Database", command=self._reset_database,
            width=150, height=35, font=ctk.CTkFont(size=12), fg_color="#b71c1c", hover_color="#c62828"
        ).pack(padx=15, pady=10, side="left")
        
        ctk.CTkButton(
            db_frame, text="Seed Demo Data", command=self._seed_data,
            width=150, height=35, font=ctk.CTkFont(size=12), fg_color="#00695c", hover_color="#00796b"
        ).pack(padx=15, pady=10, side="left")
        
        # About
        ctk.CTkLabel(
            settings_container, text="About",
            font=ctk.CTkFont(size=16, weight="bold"), text_color="#4fc3f7"
        ).pack(padx=10, pady=(15, 5), anchor="w")
        
        about_frame = ctk.CTkFrame(settings_container, fg_color="#0d1b2a", corner_radius=8)
        about_frame.pack(fill="x", padx=10, pady=5)
        
        info_text = (
            "Power Trading Analytics Desktop v1.0.0\n"
            "Cross-platform desktop application for power trading data management.\n"
            "Connects to Railway-deployed backend API for real-time data.\n"
            "Built with CustomTkinter, Matplotlib, and Python."
        )
        ctk.CTkLabel(about_frame, text=info_text, font=ctk.CTkFont(size=11), justify="left").pack(padx=15, pady=15, anchor="w")
        
    def _check_connection(self):
        """Check API connection in background"""
        def check():
            try:
                r = requests.get(f"{API_BASE_URL}/health", timeout=5)
                if r.status_code == 200:
                    self.status_dot.configure(fg_color="#4caf50")
                    self.status_label.configure(text="Connected to Railway")
                else:
                    self.status_dot.configure(fg_color="#ff9800")
                    self.status_label.configure(text=f"Status: {r.status_code}")
            except Exception as e:
                self.status_dot.configure(fg_color="#ff5252")
                self.status_label.configure(text=f"Offline - {str(e)[:30]}")
        
        threading.Thread(target=check, daemon=True).start()
    
    def _test_connection(self):
        """Test API connection"""
        def test():
            url = self.api_url_entry.get().strip()
            try:
                r = requests.get(f"{url}/health", timeout=5)
                if r.status_code == 200:
                    messagebox.showinfo("Connection Test", f"Connected successfully!\nServer: {r.json().get('status', 'unknown')}")
                else:
                    messagebox.showerror("Connection Test", f"Server returned status {r.status_code}")
            except Exception as e:
                messagebox.showerror("Connection Test", f"Failed to connect:\n{str(e)}")
        
        threading.Thread(target=test, daemon=True).start()
    
    def _load_clients(self):
        """Load clients from API"""
        def load():
            try:
                r = requests.get(f"{API_BASE_URL}/clients", timeout=10)
                if r.status_code == 200:
                    data = r.json()
                    self.clients = data.get("clients", data.get("data", []))
                    
                    # Update sidebar
                    for widget in self.client_list_frame.winfo_children():
                        widget.destroy()
                    
                    if self.clients:
                        for client in self.clients:
                            name = client.get("entity_name", client.get("name", "Unknown"))
                            entity_id = client.get("entity_id", client.get("id", ""))
                            self._add_client_button(name, entity_id)
                        
                        # Update metrics
                        self.metric_frames["clients"].configure(text=str(len(self.clients)))
                        
                        # Load transactions count
                        self._load_transactions()
                        self._load_dashboard_data()
                    else:
                        ctk.CTkLabel(
                            self.client_list_frame, text="No clients found.\nUpload a file to get started.",
                            font=ctk.CTkFont(size=11), text_color="#888"
                        ).pack(padx=10, pady=20)
                        
            except Exception as e:
                self.activity_text.configure(state="normal")
                self.activity_text.insert("1.0", f"Error loading clients: {str(e)}\n")
                self.activity_text.configure(state="disabled")
        
        threading.Thread(target=load, daemon=True).start()
    
    def _add_client_button(self, name, entity_id):
        """Add a client button to sidebar"""
        frame = ctk.CTkFrame(self.client_list_frame, fg_color="#0d1b2a", corner_radius=6)
        frame.pack(fill="x", padx=2, pady=2)
        
        btn = ctk.CTkButton(
            frame, text=f"{name[:25]}...", anchor="w",
            command=lambda eid=entity_id: self._select_client(eid),
            font=ctk.CTkFont(size=11), height=30,
            fg_color="transparent", hover_color="#1a237e",
            text_color="white"
        )
        btn.pack(side="left", fill="x", expand=True, padx=5, pady=2)
    
    def _select_client(self, entity_id):
        """Select a client"""
        self.current_client = entity_id
        self.activity_text.configure(state="normal")
        self.activity_text.insert("1.0", f"Selected client: {entity_id}\n")
        self.activity_text.configure(state="disabled")
        self._load_transactions()
    
    def _load_transactions(self):
        """Load transactions for current client"""
        def load():
            try:
                params = {}
                if self.current_client:
                    params["portfolio"] = self.current_client
                
                r = requests.get(f"{API_BASE_URL}/transactions/all", params=params, timeout=10)
                if r.status_code == 200:
                    data = r.json()
                    self.transactions = data.get("transactions", data.get("data", []))
                    
                    # Update tree
                    for item in self.tree.get_children():
                        self.tree.delete(item)
                    
                    for txn in self.transactions[:500]:  # Limit to 500 rows for performance
                        date = txn.get("trading_date", txn.get("date", ""))[:10]
                        txn_type = txn.get("transaction_type", txn.get("type", ""))
                        market = txn.get("sub_category", txn.get("market", ""))
                        qty = txn.get("quantity_mw", txn.get("quantity", 0))
                        rate = txn.get("rate_per_mwh", txn.get("rate", 0))
                        amount = txn.get("amount", 0)
                        
                        self.tree.insert("", "end", values=(
                            date, txn_type, market, 
                            f"{float(qty):.2f}" if qty else "0",
                            f"{float(rate):.2f}" if rate else "0",
                            f"{float(amount):.2f}" if amount else "0"
                        ))
                    
                    # Update metrics
                    self.metric_frames["transactions"].configure(text=str(len(self.transactions)))
                    
            except Exception as e:
                pass
        
        threading.Thread(target=load, daemon=True).start()
    
    def _load_dashboard_data(self):
        """Load dashboard analytics data"""
        def load():
            try:
                r = requests.get(f"{API_BASE_URL}/analytics/summary", timeout=10)
                if r.status_code == 200:
                    data = r.json()
                    summary = data.get("summary", {})
                    
                    # Update charts
                    hourly = data.get("hourly_distribution", [])
                    if hourly:
                        hours = [h.get("hour", h.get("time_block", "")) for h in hourly]
                        buy_vals = [float(h.get("buy_volume", 0)) for h in hourly]
                        sell_vals = [float(h.get("sell_volume", 0)) for h in hourly]
                        
                        self.ax1.clear()
                        self.ax1.set_facecolor("#0d1b2a")
                        self.ax1.bar(range(len(hours)), buy_vals, label="Buy", color="#4fc3f7", alpha=0.7)
                        self.ax1.bar(range(len(hours)), sell_vals, label="Sell", color="#ef5350", alpha=0.7)
                        self.ax1.legend()
                        self.ax1.tick_params(colors="white")
                        self.ax1.spines["bottom"].set_color("#444")
                        self.ax1.spines["left"].set_color("#444")
                        self.canvas1.draw()
                    
                    # Portfolio comparison
                    portfolio_comp = data.get("portfolio_comparison", [])
                    if portfolio_comp:
                        names = [p.get("portfolio", p.get("name", "Unknown"))[:10] for p in portfolio_comp]
                        values = [float(p.get("total_amount", p.get("volume", 0))) for p in portfolio_comp]
                        
                        self.ax2.clear()
                        self.ax2.set_facecolor("#0d1b2a")
                        colors = ["#4fc3f7", "#ef5350", "#66bb6a", "#ffa726", "#ab47bc"]
                        self.ax2.pie(values, labels=names, autopct="%1.0f%%", 
                                     colors=colors[:len(values)], textprops={"color": "white"})
                        self.canvas2.draw()
                    
                    # Update analytics labels
                    self.analytics_labels["buy_vol"].configure(
                        text=f"{float(summary.get('total_buy_volume', 0)):.2f} MWh")
                    self.analytics_labels["sell_vol"].configure(
                        text=f"{float(summary.get('total_sell_volume', 0)):.2f} MWh")
                    
                    net = float(summary.get("net_amount", 0))
                    self.analytics_labels["net_amt"].configure(
                        text=f"Rs {net:,.2f}")
                    
                    self.analytics_labels["avg_rate"].configure(
                        text=f"Rs {float(summary.get('avg_rate', 0)):.2f}/MWh")
                    
                    # Update hourly chart in analytics
                    if hourly:
                        self.ax3.clear()
                        self.ax3.set_facecolor("#0d1b2a")
                        hours_display = [h.get("hour", h.get("time_block", ""))[:5] for h in hourly]
                        buy_v = [float(h.get("buy_volume", 0)) for h in hourly]
                        self.ax3.plot(range(len(hours_display)), buy_v, color="#4fc3f7", marker="o", linewidth=1)
                        self.ax3.fill_between(range(len(hours_display)), buy_v, alpha=0.3, color="#4fc3f7")
                        self.ax3.tick_params(colors="white")
                        self.ax3.spines["bottom"].set_color("#444")
                        self.ax3.spines["left"].set_color("#444")
                        self.canvas3.draw()
                    
                    # Market breakdown
                    market_data = summary.get("market_breakdown", {})
                    if market_data:
                        self.ax4.clear()
                        self.ax4.set_facecolor("#0d1b2a")
                        markets = list(market_data.keys())
                        m_vals = [float(market_data[m]) for m in markets]
                        m_colors = ["#4fc3f7", "#66bb6a", "#ffa726"]
                        self.ax4.barh(markets, m_vals, color=m_colors[:len(markets)])
                        self.ax4.tick_params(colors="white")
                        self.ax4.spines["bottom"].set_color("#444")
                        self.ax4.spines["left"].set_color("#444")
                        self.canvas4.draw()
                        
            except Exception as e:
                pass
        
        threading.Thread(target=load, daemon=True).start()
    
    def _upload_file(self):
        """Upload Excel file"""
        file_path = filedialog.askopenfilename(
            title="Select Excel File",
            filetypes=[("Excel files", "*.xls;*.xlsx"), ("All files", "*.*")]
        )
        
        if not file_path:
            return
        
        def upload():
            try:
                self.upload_btn.configure(text="Uploading...", state="disabled")
                
                with open(file_path, "rb") as f:
                    files = {"file": (os.path.basename(file_path), f, "application/vnd.ms-excel")}
                    r = requests.post(f"{API_BASE_URL}/upload", files=files, timeout=30)
                
                self.upload_btn.configure(text="Upload Excel File", state="normal")
                
                if r.status_code == 200:
                    data = r.json()
                    result = data.get("summary", data)
                    
                    msg = f"File uploaded successfully!\n"
                    msg += f"Entity: {result.get('entity', 'Unknown')}\n"
                    msg += f"Transactions: {result.get('buy_transactions', 0) + result.get('sell_transactions', 0)}"
                    
                    messagebox.showinfo("Upload Success", msg)
                    
                    # Reload data
                    self._load_clients()
                    self._load_dashboard_data()
                else:
                    error = r.json().get("detail", str(r.text))
                    messagebox.showerror("Upload Failed", f"Error: {error}")
                    
            except Exception as e:
                self.upload_btn.configure(text="Upload Excel File", state="normal")
                messagebox.showerror("Upload Error", f"Connection failed:\n{str(e)}")
        
        threading.Thread(target=upload, daemon=True).start()
    
    def _apply_filters(self):
        """Apply transaction filters"""
        self._load_transactions()
    
    def _export_csv(self):
        """Export transactions to CSV"""
        if not self.transactions:
            messagebox.showinfo("Export", "No transactions to export.")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Save CSV", defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")]
        )
        
        if not file_path:
            return
        
        try:
            df = pd.DataFrame(self.transactions)
            df.to_csv(file_path, index=False)
            messagebox.showinfo("Export Successful", f"Exported {len(self.transactions)} transactions to:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Export Failed", str(e))
    
    def _generate_report(self):
        """Generate a report"""
        messagebox.showinfo("Report", "Report generation feature coming soon.\nThis will generate PDF reports of trading activity.")
    
    def _view_all_transactions(self):
        """Switch to transactions tab"""
        self.tab_view.set("Transactions")
    
    def _view_energy_schedule(self):
        """View energy schedule"""
        def load():
            try:
                r = requests.get(f"{API_BASE_URL}/energy-schedule/status", timeout=10)
                if r.status_code == 200:
                    data = r.json()
                    days = data.get("days_calculated", data.get("count", 0))
                    if days:
                        messagebox.showinfo("Energy Schedule", f"Energy Schedule Status:\n{data}")
                    else:
                        messagebox.showinfo("Energy Schedule", "No energy schedule data available.\nUpload DOR and SCH files to calculate.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load: {str(e)}")
        
        threading.Thread(target=load, daemon=True).start()
    
    def _refresh_data(self):
        """Refresh all data"""
        self.refresh_btn.configure(text="Loading...", state="disabled")
        self._check_connection()
        self._load_clients()
        
        self.window.after(2000, lambda: self.refresh_btn.configure(text="Refresh", state="normal"))
    
    def _reset_database(self):
        """Reset the database"""
        if not messagebox.askyesno("Confirm Reset", 
            "Are you sure you want to reset the database?\nThis will DELETE ALL DATA!"):
            return
        
        def reset():
            try:
                r = requests.post(f"{API_BASE_URL}/admin/reset-database", timeout=15)
                if r.status_code == 200:
                    data = r.json()
                    deleted = data.get("deleted", {})
                    msg = f"Database reset complete!\nDeleted: {json.dumps(deleted)}"
                    messagebox.showinfo("Reset Complete", msg)
                    self._load_clients()
                else:
                    messagebox.showerror("Reset Failed", f"Status: {r.status_code}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to reset: {str(e)}")
        
        threading.Thread(target=reset, daemon=True).start()
    
    def _seed_data(self):
        """Seed demo data"""
        messagebox.showinfo("Seed Data", "Seeding demo data from Railway server...\nThis may take a minute.")
        
        def seed():
            try:
                r = requests.post(f"{API_BASE_URL}/admin/seed-demo", timeout=120)
                if r.status_code == 200:
                    messagebox.showinfo("Seed Complete", "Demo data loaded successfully!")
                    self._load_clients()
                else:
                    # Try via direct generate_mock_reports approach
                    messagebox.showinfo("Info", "Server seed not available. Please upload files manually.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to seed: {str(e)}")
        
        threading.Thread(target=seed, daemon=True).start()
    
    def run(self):
        """Run the desktop application"""
        self.window.mainloop()


if __name__ == "__main__":
    app = PowerTradingDesktopApp()
    app.run()