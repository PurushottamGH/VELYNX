"""
VELYNX Simulation Engine — Phase 35
Dual output: ASCII terminal preview + Interactive 3D HTML browser
"""
from __future__ import annotations
import numpy as np
import os
import time
import webbrowser
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

OUTPUT_DIR = Path("velynx_output")
OUTPUT_DIR.mkdir(exist_ok=True)


@dataclass
class SimResult:
    html_path: str
    ascii_preview: str
    sim_type: str
    title: str
    opened: bool = False
    error: Optional[str] = None


class SimEngine:

    def run(self, sim_type: str, params: dict) -> SimResult:
        try:
            handlers = {
                "orbital": self.orbital_simulation,
                "wave": self.wave_simulation,
                "molecular": self.molecular_structure,
                "solar_system": self.solar_system,
                "projectile": self.projectile_motion,
                "pendulum": self.pendulum_simulation,
            }
            fn = handlers.get(sim_type, self.orbital_simulation)
            return fn(params)
        except Exception as e:
            return SimResult(html_path="", ascii_preview="Simulation failed",
                             sim_type=sim_type, title="Error", error=str(e))

    # ── 1. Orbital Simulation ─────────────────────────────────────────

    def orbital_simulation(self, params: dict) -> SimResult:
        import plotly.graph_objects as go
        G = 6.674e-11
        mass_star = params.get("mass_star", 2e30)
        v0 = params.get("velocity", 29780.0)
        dt = params.get("dt", 3600 * 24)
        steps = params.get("steps", 365)

        x, y, z = 1.496e11, 0.0, 0.0
        vx, vy, vz = 0.0, v0, 0.0
        xs, ys, zs = [x], [y], [z]

        for _ in range(steps):
            r = np.sqrt(x**2 + y**2 + z**2)
            ax = -G * mass_star * x / r**3
            ay = -G * mass_star * y / r**3
            az = -G * mass_star * z / r**3
            vx += ax * dt; vy += ay * dt; vz += az * dt
            x += vx * dt; y += vy * dt; z += vz * dt
            xs.append(x); ys.append(y); zs.append(z)

        AU = 1.496e11
        xs = [v/AU for v in xs]; ys = [v/AU for v in ys]; zs = [v/AU for v in zs]

        frames = []
        step = max(1, len(xs)//60)
        for i in range(0, len(xs), step):
            frames.append(go.Frame(data=[
                go.Scatter3d(x=xs[:i+1], y=ys[:i+1], z=zs[:i+1], mode="lines",
                             line=dict(color="cyan", width=2), name="Orbit trail"),
                go.Scatter3d(x=[xs[i]], y=[ys[i]], z=[zs[i]], mode="markers",
                             marker=dict(size=8, color="blue"), name="Planet"),
            ], name=str(i)))

        fig = go.Figure(
            data=[
                go.Scatter3d(x=[0], y=[0], z=[0], mode="markers",
                             marker=dict(size=20, color="yellow"), name="Star"),
                go.Scatter3d(x=xs, y=ys, z=zs, mode="lines",
                             line=dict(color="cyan", width=1, dash="dot"), opacity=0.4),
                go.Scatter3d(x=[xs[0]], y=[ys[0]], z=[zs[0]], mode="markers",
                             marker=dict(size=8, color="blue"), name="Planet"),
            ],
            frames=frames,
            layout=go.Layout(
                title="Orbital Mechanics Simulation",
                scene=dict(bgcolor="black", xaxis=dict(title="X (AU)", color="white", gridcolor="#333"),
                           yaxis=dict(title="Y (AU)", color="white", gridcolor="#333"),
                           zaxis=dict(title="Z (AU)", color="white", gridcolor="#333")),
                paper_bgcolor="black", font=dict(color="white"),
                updatemenus=[dict(type="buttons", buttons=[
                    dict(label="Play", method="animate", args=[None, {"frame": {"duration": 50}}]),
                    dict(label="Pause", method="animate", args=[[None], {"mode": "immediate"}]),
                ], bgcolor="#333", font=dict(color="white"))],
            )
        )

        path = self._save(fig, "orbital_simulation")
        ascii_prev = self._orbital_ascii(xs, ys)
        return SimResult(html_path=path, ascii_preview=ascii_prev,
                         sim_type="orbital", title="Orbital Mechanics")

    def _orbital_ascii(self, xs, ys) -> str:
        W, H = 40, 20
        grid = [[" "] * W for _ in range(H)]
        max_r = max(max(abs(x) for x in xs), max(abs(y) for y in ys)) or 1
        step = max(1, len(xs) // 100)
        for i in range(0, len(xs), step):
            gx = int((xs[i] / max_r + 1) / 2 * (W - 1))
            gy = int((ys[i] / max_r + 1) / 2 * (H - 1))
            if 0 <= gx < W and 0 <= gy < H:
                grid[gy][gx] = "."
        cx, cy = W // 2, H // 2
        grid[cy][cx] = "*"
        grid[int((ys[0]/max_r+1)/2*(H-1))][int((xs[0]/max_r+1)/2*(W-1))] = "o"
        lines = ["  +" + "-"*W + "+"]
        for row in grid:
            lines.append("  |" + "".join(row) + "|")
        lines.append("  +" + "-"*W + "+")
        lines.append("  *=Star  o=Planet  .=Orbit path")
        return "\n".join(lines)

    # ── 2. Wave Simulation ────────────────────────────────────────────

    def wave_simulation(self, params: dict) -> SimResult:
        import plotly.graph_objects as go
        wave_type = params.get("wave_type", "sine")
        freq = params.get("frequency", 1.0)
        amp = params.get("amplitude", 1.0)
        n_frames = params.get("frames", 60)

        x = np.linspace(0, 4 * np.pi, 500)
        frames = []
        for t in np.linspace(0, 2*np.pi, n_frames):
            if wave_type == "standing":
                y = amp * np.sin(freq * x) * np.cos(t); color = "cyan"
            elif wave_type == "interference":
                y = amp * np.sin(freq * x - t) + amp * np.sin(freq * x - t + 0.5); color = "magenta"
            elif wave_type == "em":
                y = amp * np.sin(freq * x - t); z = amp * np.cos(freq * x - t)
            else:
                y = amp * np.sin(freq * x - t); color = "lime"

            if wave_type == "em":
                frames.append(go.Frame(data=[
                    go.Scatter3d(x=x, y=y, z=np.zeros_like(x), mode="lines",
                                 line=dict(color="cyan", width=3), name="E field"),
                    go.Scatter3d(x=x, y=np.zeros_like(x), z=z, mode="lines",
                                 line=dict(color="magenta", width=3), name="B field"),
                ]))
            else:
                frames.append(go.Frame(data=[
                    go.Scatter(x=x, y=y, mode="lines", line=dict(color=color, width=3))
                ]))

        if wave_type == "em":
            init_data = [go.Scatter3d(x=x, y=np.sin(x), z=np.zeros_like(x), mode="lines",
                                       line=dict(color="cyan", width=3)),
                         go.Scatter3d(x=x, y=np.zeros_like(x), z=np.cos(x), mode="lines",
                                       line=dict(color="magenta", width=3))]
            layout = go.Layout(title="Electromagnetic Wave", scene=dict(bgcolor="black"),
                               paper_bgcolor="black", font=dict(color="white"))
        else:
            init_data = [go.Scatter(x=x, y=np.sin(x), mode="lines",
                                     line=dict(color="lime", width=3))]
            layout = go.Layout(title=f"{wave_type.title()} Wave", xaxis=dict(color="white", gridcolor="#333"),
                               yaxis=dict(color="white", gridcolor="#333", range=[-2.5, 2.5]),
                               paper_bgcolor="black", plot_bgcolor="#111", font=dict(color="white"))

        fig = go.Figure(data=init_data, frames=frames, layout=layout)
        fig.layout.updatemenus = [dict(type="buttons", buttons=[
            dict(label="Play", method="animate", args=[None, {"frame": {"duration": 50}}]),
            dict(label="Pause", method="animate", args=[[None], {"mode": "immediate"}]),
        ], bgcolor="#333", font=dict(color="white"))]

        path = self._save(fig, f"wave_{wave_type}")
        return SimResult(html_path=path, ascii_preview=self._wave_ascii(wave_type),
                         sim_type="wave", title=f"{wave_type.title()} Wave")

    def _wave_ascii(self, wave_type: str) -> str:
        x = np.linspace(0, 4*np.pi, 60)
        y = np.sin(x)
        H = 9
        lines = ["  +" + "-"*60 + "+"]
        for row in range(H):
            threshold = 1 - (row / (H-1)) * 2
            line = "".join("~" if abs(val - threshold) < 2/H else " " for val in y)
            lines.append(f"  |{line}|")
        lines.append("  +" + "-"*60 + "+")
        lines.append(f"  {wave_type.title()} wave")
        return "\n".join(lines)

    # ── 3. Molecular Structure ────────────────────────────────────────

    def molecular_structure(self, params: dict) -> SimResult:
        import plotly.graph_objects as go
        molecule = params.get("molecule", "H2O").upper()

        MOLECULES = {
            "H2O": {"atoms": [("O", 0, 0, 0, "red", 20), ("H", 0.96, 0, 0, "white", 10),
                               ("H", -0.24, 0.93, 0, "white", 10)],
                    "bonds": [(0,1), (0,2)], "name": "Water (H2O)"},
            "CO2": {"atoms": [("C", 0, 0, 0, "gray", 15), ("O", 1.16, 0, 0, "red", 18),
                               ("O", -1.16, 0, 0, "red", 18)],
                    "bonds": [(0,1), (0,2)], "name": "Carbon Dioxide (CO2)"},
            "CH4": {"atoms": [("C", 0, 0, 0, "gray", 15), ("H", 0.63, 0.63, 0.63, "white", 10),
                               ("H", -0.63,-0.63, 0.63, "white", 10), ("H", -0.63, 0.63,-0.63, "white", 10),
                               ("H", 0.63,-0.63,-0.63, "white", 10)],
                    "bonds": [(0,1),(0,2),(0,3),(0,4)], "name": "Methane (CH4)"},
            "NH3": {"atoms": [("N", 0, 0, 0, "blue", 18), ("H", 0.94, 0, -0.33, "white", 10),
                               ("H", -0.47, 0.82,-0.33, "white", 10), ("H", -0.47,-0.82,-0.33, "white", 10)],
                    "bonds": [(0,1),(0,2),(0,3)], "name": "Ammonia (NH3)"},
        }

        mol = MOLECULES.get(molecule, MOLECULES["H2O"])
        atoms = mol["atoms"]
        traces = []
        for sym, x, y, z, color, size in atoms:
            traces.append(go.Scatter3d(x=[x], y=[y], z=[z], mode="markers+text",
                                        marker=dict(size=size, color=color, line=dict(color="gray", width=1)),
                                        text=[sym], textposition="top center", name=sym))
        for i, j in mol["bonds"]:
            _, x1,y1,z1,_,_ = atoms[i]; _, x2,y2,z2,_,_ = atoms[j]
            traces.append(go.Scatter3d(x=[x1,x2], y=[y1,y2], z=[z1,z2], mode="lines",
                                        line=dict(color="white", width=6), showlegend=False))

        fig = go.Figure(data=traces, layout=go.Layout(
            title=f"{mol['name']} Molecular Structure",
            scene=dict(bgcolor="black", xaxis=dict(color="white", gridcolor="#222"),
                       yaxis=dict(color="white", gridcolor="#222"), zaxis=dict(color="white", gridcolor="#222")),
            paper_bgcolor="black", font=dict(color="white")))

        path = self._save(fig, f"molecule_{molecule}")
        lines = [f"  +-------------------------+",
                 f"  |  Molecule: {molecule:<13} |",
                 f"  |  Atoms: {len(atoms):<16} |"]
        for sym, x, y, z, _, _ in atoms:
            lines.append(f"  |  {sym}  ({x:+.2f}, {y:+.2f}, {z:+.2f})  |")
        lines.append(f"  +-------------------------+")
        return SimResult(html_path=path, ascii_preview="\n".join(lines),
                         sim_type="molecular", title=mol["name"])

    # ── 4. Solar System ───────────────────────────────────────────────

    def solar_system(self, params: dict) -> SimResult:
        import plotly.graph_objects as go
        PLANETS = [("Mercury", 0.387, 88, 4, "gray"), ("Venus", 0.723, 225, 9, "orange"),
                   ("Earth", 1.000, 365, 10, "blue"), ("Mars", 1.524, 687, 7, "red"),
                   ("Jupiter", 5.203, 4333, 25, "brown"), ("Saturn", 9.537, 10759, 20, "gold"),
                   ("Uranus", 19.19, 30687, 15, "lightblue"), ("Neptune", 30.07, 60190, 14, "darkblue")]
        if params.get("focus", "inner") == "inner":
            PLANETS = PLANETS[:4]

        n_frames = 120
        frames = []
        for fi in range(n_frames):
            t = fi / n_frames * 2 * np.pi
            data = [go.Scatter(x=[0], y=[0], mode="markers", marker=dict(size=25, color="yellow"), name="Sun")]
            for name, dist, period, size, color in PLANETS:
                angle = t * (365 / period)
                data.append(go.Scatter(x=[dist*np.cos(angle)], y=[dist*np.sin(angle)],
                                        mode="markers+text", marker=dict(size=size, color=color),
                                        text=[name[0]], textposition="top center", name=name))
            frames.append(go.Frame(data=data, name=str(fi)))

        init_data = [go.Scatter(x=[0], y=[0], mode="markers", marker=dict(size=25, color="yellow"), name="Sun")]
        for name, dist, _, size, color in PLANETS:
            init_data.append(go.Scatter(x=[dist], y=[0], mode="markers+text",
                                         marker=dict(size=size, color=color), text=[name], name=name))

        lim = PLANETS[-1][1] * 1.2
        fig = go.Figure(data=init_data, frames=frames, layout=go.Layout(
            title="Solar System", xaxis=dict(range=[-lim,lim], color="white", gridcolor="#222", title="AU"),
            yaxis=dict(range=[-lim,lim], color="white", gridcolor="#222", title="AU", scaleanchor="x"),
            paper_bgcolor="black", plot_bgcolor="black", font=dict(color="white"),
            updatemenus=[dict(type="buttons", buttons=[
                dict(label="Play", method="animate", args=[None, {"frame": {"duration": 50}}]),
                dict(label="Pause", method="animate", args=[[None], {"mode": "immediate"}]),
            ], bgcolor="#333", font=dict(color="white"))]))

        path = self._save(fig, "solar_system")
        lines = ["  +--------------------------------+",
                 "  |        *  SOLAR SYSTEM  *      |",
                 "  +------------+----------+--------+",
                 "  | Planet     | Dist(AU) | Period |",
                 "  +------------+----------+--------+"]
        for name, dist, period, _, _ in PLANETS:
            lines.append(f"  | {name:<10} | {dist:<8.3f} | {period:<6}d|")
        lines.append("  +------------+----------+--------+")
        return SimResult(html_path=path, ascii_preview="\n".join(lines),
                         sim_type="solar_system", title="Solar System")

    # ── 5. Projectile Motion ──────────────────────────────────────────

    def projectile_motion(self, params: dict) -> SimResult:
        import plotly.graph_objects as go
        angle_deg = params.get("angle", 45); v0 = params.get("velocity", 50); g = 9.81
        angle_rad = np.radians(angle_deg)
        vx = v0 * np.cos(angle_rad); vy = v0 * np.sin(angle_rad)
        t_flight = 2 * vy / g
        t = np.linspace(0, t_flight, 300)
        x = vx * t; y = np.maximum(vy * t - 0.5 * g * t**2, 0)
        max_h = (vy**2) / (2*g); range_m = (v0**2 * np.sin(2*angle_rad)) / g

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=x, y=y, mode="lines", line=dict(color="cyan", width=3), name="Trajectory"))
        fig.add_trace(go.Scatter(x=[x[len(x)//2]], y=[max_h], mode="markers+text",
                                  marker=dict(size=10, color="yellow"), text=[f"Peak: {max_h:.1f}m"],
                                  textposition="top center", name="Peak"))
        fig.update_layout(title=f"Projectile: {angle_deg} deg at {v0}m/s",
                          xaxis=dict(title="Distance (m)", color="white", gridcolor="#333"),
                          yaxis=dict(title="Height (m)", color="white", gridcolor="#333"),
                          paper_bgcolor="black", plot_bgcolor="#111", font=dict(color="white"),
                          annotations=[dict(x=range_m*0.5, y=max_h*1.1,
                                            text=f"Range: {range_m:.1f}m | Height: {max_h:.1f}m | Time: {t_flight:.1f}s",
                                            font=dict(color="white"), showarrow=False)])

        path = self._save(fig, "projectile_motion")
        W, H = 50, 12; grid = [[" "]*W for _ in range(H)]
        mx = max(x) or 1; my = max(y) or 1
        for xi, yi in zip(x, y):
            gx = int(xi/mx*(W-1)); gy = H-1-int(yi/my*(H-1))
            if 0 <= gx < W and 0 <= gy < H: grid[gy][gx] = "."
        grid[H-1] = ["_"]*W
        lines = ["  +" + "-"*W + "+"]
        for row in grid: lines.append("  |" + "".join(row) + "|")
        lines.append("  +" + "-"*W + "+")
        return SimResult(html_path=path, ascii_preview="\n".join(lines),
                         sim_type="projectile", title=f"Projectile {angle_deg}deg {v0}m/s")

    # ── 6. Pendulum ───────────────────────────────────────────────────

    def pendulum_simulation(self, params: dict) -> SimResult:
        import plotly.graph_objects as go
        from scipy.integrate import solve_ivp
        L1 = params.get("L1", 1.0); L2 = params.get("L2", 1.0)
        m1 = params.get("m1", 1.0); m2 = params.get("m2", 1.0)
        th1 = params.get("theta1", np.pi/2); th2 = params.get("theta2", np.pi/2 + 0.01)
        g = 9.81

        def deriv(t, y):
            th1, w1, th2, w2 = y
            d = th2 - th1
            den1 = (m1+m2)*L1 - m2*L1*np.cos(d)**2
            den2 = (L2/L1)*den1
            dth1 = w1
            dw1 = (m2*L1*w1**2*np.sin(d)*np.cos(d) + m2*g*np.sin(th2)*np.cos(d)
                   + m2*L2*w2**2*np.sin(d) - (m1+m2)*g*np.sin(th1)) / den1
            dth2 = w2
            dw2 = (-m2*L2*w2**2*np.sin(d)*np.cos(d) + (m1+m2)*(g*np.sin(th1)*np.cos(d)
                   - L1*w1**2*np.sin(d) - g*np.sin(th2))) / den2
            return [dth1, dw1, dth2, dw2]

        sol = solve_ivp(deriv, [0,20], [th1,0,th2,0],
                        t_eval=np.linspace(0,20,500), method="RK45")
        x1 = L1*np.sin(sol.y[0]); y1 = -L1*np.cos(sol.y[0])
        x2 = x1 + L2*np.sin(sol.y[2]); y2 = y1 - L2*np.cos(sol.y[2])

        frames = []
        step = max(1, len(x1)//80)
        for i in range(0, len(x1), step):
            frames.append(go.Frame(data=[
                go.Scatter(x=[0,x1[i]], y=[0,y1[i]], mode="lines",
                           line=dict(color="white", width=3)),
                go.Scatter(x=[x1[i],x2[i]], y=[y1[i],y2[i]], mode="lines+markers",
                           line=dict(color="white", width=3),
                           marker=dict(size=[12,12], color=["cyan","magenta"])),
                go.Scatter(x=x2[:i+1], y=y2[:i+1], mode="lines",
                           line=dict(color="magenta", width=1), opacity=0.5),
            ], name=str(i)))

        fig = go.Figure(data=[
            go.Scatter(x=[0,x1[0]], y=[0,y1[0]], mode="lines",
                       line=dict(color="white", width=3)),
            go.Scatter(x=[x1[0],x2[0]], y=[y1[0],y2[0]], mode="lines+markers",
                       line=dict(color="white", width=3),
                       marker=dict(size=[12,12], color=["cyan","magenta"])),
        ], frames=frames, layout=go.Layout(
            title="Double Pendulum Chaos", xaxis=dict(range=[-2.5,2.5], color="white", gridcolor="#333", scaleanchor="y"),
            yaxis=dict(range=[-2.5,2.5], color="white", gridcolor="#333"),
            paper_bgcolor="black", plot_bgcolor="#111", font=dict(color="white"),
            updatemenus=[dict(type="buttons", buttons=[
                dict(label="Play", method="animate", args=[None,{"frame":{"duration":30}}]),
                dict(label="Pause", method="animate", args=[[None],{"mode":"immediate"}]),
            ], bgcolor="#333", font=dict(color="white"))]))

        path = self._save(fig, "pendulum_chaos")
        ascii_prev = ("  +--------------------------+\n"
                      "  |   Double Pendulum Chaos  |\n"
                      "  |         0                |\n"
                      "  |         |                |\n"
                      "  |         o  <- m1          |\n"
                      "  |          \\               |\n"
                      "  |           o  <- m2        |\n"
                      "  |    (chaotic motion)      |\n"
                      "  +--------------------------+")
        return SimResult(html_path=path, ascii_preview=ascii_prev,
                         sim_type="pendulum", title="Double Pendulum Chaos")

    # ── Helpers ───────────────────────────────────────────────────────

    def _save(self, fig, name: str) -> str:
        slug = name.replace(" ", "_")
        path = OUTPUT_DIR / f"sim_{slug}_{int(time.time())}.html"
        fig.write_html(str(path), include_plotlyjs="cdn", full_html=True)
        return str(path)


sim_engine = SimEngine()
