import os
import csv
import json
import http.server
import socketserver
import webbrowser
import threading

def ensure_dirs():
    for d in ['data', 'js', 'css']:
        os.makedirs(d, exist_ok=True)

def clean_url(url):
    url = url.strip()
    if url and not url.startswith('http'):
        return 'https://' + url
    return url

def sanitize_data(csv_path='data.csv', json_path='data/students.json'):
    print(f"Sanitizing {csv_path} to {json_path}...")
    students = []
    
    if not os.path.exists(csv_path):
        print(f"Error: {csv_path} not found.")
        return

    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.reader(f)
        headers = next(reader, None)
        
        for row in reader:
            if len(row) < 18:
                continue
                
            raw_name = row[1].strip()
            name = raw_name.split(' - ')[-1] if ' - ' in raw_name else raw_name
            
            raw_cgpa = row[4].strip()
            try:
                cgpa = float(raw_cgpa) if raw_cgpa != '-' else 0.0
            except:
                cgpa = 0.0
                
            raw_backlogs = row[5].strip().lower()
            backlogs = 0 if 'no backlogs' in raw_backlogs else (1 if 'active' in raw_backlogs else 0)
            
            domains = [d.strip() for d in row[7].split(',') if d.strip()]
            
            internship_raw = row[11].strip().lower()
            has_internship = 'yes' in internship_raw or len(internship_raw) > 5
            
            cert_raw = row[12].strip().lower()
            has_cert = 'yes' in cert_raw or len(cert_raw) > 10
            
            tech_stack = [t.strip() for t in row[13].split(',') if t.strip()]
            
            try:
                comfort = int(row[14].strip())
            except:
                comfort = 3
                
            self_learn_raw = row[15].strip()
            self_learn_score = 0
            if '61' in self_learn_raw:
                self_learn_score = 20
            elif '26' in self_learn_raw:
                self_learn_score = 10
                
            showcase_raw = row[16].strip().lower()
            showcase_score = 0
            if 'fully updated' in showcase_raw:
                showcase_score = 15
            elif 'needs some minor' in showcase_raw:
                showcase_score = 7
                
            # Composite Readiness Score
            cgpa_score = min((cgpa / 10.0) * 30, 30)
            internship_score = 15 if has_internship else 0
            cert_score = 10 if has_cert else 0
            comfort_score = comfort * 2
            
            readiness = round(cgpa_score + internship_score + cert_score + self_learn_score + showcase_score + comfort_score)
            readiness = min(readiness, 100)
            
            student = {
                'name': name,
                'cgpa': cgpa,
                'active_backlogs': backlogs,
                'domains': domains,
                'tech_stack': tech_stack,
                'has_internship': has_internship,
                'has_cert': has_cert,
                'internship_details': internship_raw,
                'cert_details': cert_raw,
                'comfort_level': comfort,
                'self_learning': self_learn_raw,
                'showcase': showcase_raw,
                'adaptability': row[17].strip() if len(row)>17 else '',
                'time_spent': row[18].strip() if len(row)>18 else '',
                'portfolio_readiness': readiness,
                'github': clean_url(row[9]),
                'linkedin': clean_url(row[8]),
                'resume': clean_url(row[10]),
                'phone': row[2].strip() if len(row)>2 else '',
                'email': row[3].strip() if len(row)>3 else ''
            }
            students.append(student)
            
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(students, f, indent=2)

def generate_static_files():
    # css/style.css
    with open('css/style.css', 'w', encoding='utf-8') as f:
        f.write("""
body {
    font-family: 'Inter', sans-serif;
    background-color: #fafafa;
    background-image: radial-gradient(circle at 10% 20%, rgba(220, 38, 38, 0.03) 0%, transparent 40%),
                      radial-gradient(circle at 90% 80%, rgba(220, 38, 38, 0.04) 0%, transparent 40%);
    color: #1e293b;
}
.glass-panel {
    background: rgba(255, 255, 255, 0.7);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1px solid rgba(220, 38, 38, 0.08);
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.03);
}
.table-container {
    max-height: 500px;
    overflow-y: auto;
}
.table-container::-webkit-scrollbar { width: 6px; height: 6px; }
.table-container::-webkit-scrollbar-track { background: transparent; }
.table-container::-webkit-scrollbar-thumb { background: rgba(220, 38, 38, 0.2); border-radius: 4px; }
.table-container::-webkit-scrollbar-thumb:hover { background: rgba(220, 38, 38, 0.5); }

thead th {
    position: sticky;
    top: 0;
    background: rgba(255, 255, 255, 0.95);
    z-index: 10;
    backdrop-filter: blur(10px);
}
.badge {
    padding: 0.125rem 0.5rem;
    border-radius: 9999px;
    font-size: 0.7rem;
    font-weight: 600;
}
/* Adapting all badges to Red/White minimalism */
.badge-blue { background-color: rgba(220, 38, 38, 0.05); color: #dc2626; border: 1px solid rgba(220, 38, 38, 0.15); }
.badge-purple { background-color: rgba(153, 27, 27, 0.05); color: #991b1b; border: 1px solid rgba(153, 27, 27, 0.15); }
.badge-green { background-color: rgba(34, 197, 94, 0.1); color: #166534; border: 1px solid rgba(34, 197, 94, 0.2); }
.badge-red { background-color: rgba(220, 38, 38, 0.1); color: #b91c1c; border: 1px solid rgba(220, 38, 38, 0.2); }
.badge-amber { background-color: rgba(225, 29, 72, 0.05); color: #be123c; border: 1px solid rgba(225, 29, 72, 0.15); }

/* Modal */
#student-modal {
    transition: opacity 0.3s ease;
}
        """)

    # js/charts.js
    with open('js/charts.js', 'w', encoding='utf-8') as f:
        f.write("""
let scatterChart, radarChart, donutChart;

function initCharts(students) {
    Chart.defaults.color = '#64748b';
    Chart.defaults.font.family = 'Inter';

    // 1. Scatter Chart (CGPA vs Readiness)
    const scatterData = students.map(s => ({x: s.cgpa, y: s.portfolio_readiness, r: 6, name: s.name}));
    
    const ctxScatter = document.getElementById('scatterChart').getContext('2d');
    if(scatterChart) scatterChart.destroy();
    scatterChart = new Chart(ctxScatter, {
        type: 'bubble',
        data: {
            datasets: [{
                label: 'Students',
                data: scatterData,
                backgroundColor: 'rgba(220, 38, 38, 0.6)',
                borderColor: 'rgba(220, 38, 38, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: (ctx) => `${ctx.raw.name}: CGPA ${ctx.raw.x}, Score ${ctx.raw.y}`
                    }
                }
            },
            onClick: (e, elements) => {
                if (elements.length > 0) {
                    const idx = elements[0].index;
                    const studentName = scatterData[idx].name;
                    const student = window.allStudents.find(s => s.name === studentName);
                    if(student && window.openModal) window.openModal(student);
                } else {
                    alert("Dashboard Purpose: Evaluate placement readiness across technical and behavioral matrices.\\n\\nFor queries, contact Admin:\\nEmail: placement@college.edu\\nPhone: +91-9876543210");
                }
            },
            scales: {
                x: { title: {display: true, text: 'CGPA'}, min: 5, max: 10, grid: { color: 'rgba(0,0,0,0.04)' } },
                y: { title: {display: true, text: 'Readiness Score'}, min: 0, max: 100, grid: { color: 'rgba(0,0,0,0.04)' } }
            }
        }
    });

    // 2. Radar Chart (Cohort Average Skills/Domains)
    const domainScores = {};
    students.forEach(s => {
        s.domains.forEach(d => {
            domainScores[d] = (domainScores[d] || 0) + 1;
        });
    });
    
    const topDomains = Object.entries(domainScores).sort((a,b) => b[1] - a[1]).slice(0, 6);
    
    const ctxRadar = document.getElementById('radarChart').getContext('2d');
    if(radarChart) radarChart.destroy();
    radarChart = new Chart(ctxRadar, {
        type: 'radar',
        data: {
            labels: topDomains.map(d => d[0]),
            datasets: [{
                label: 'Domain Interest Volume',
                data: topDomains.map(d => d[1]),
                backgroundColor: 'rgba(225, 29, 72, 0.1)',
                borderColor: 'rgba(225, 29, 72, 0.8)',
                pointBackgroundColor: 'rgba(225, 29, 72, 1)',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                r: {
                    angleLines: { color: 'rgba(0,0,0,0.05)' },
                    grid: { color: 'rgba(0,0,0,0.05)' },
                    pointLabels: { color: '#475569', font: {size: 10} },
                    ticks: { display: false }
                }
            },
            onClick: (e, elements) => {
                alert("Dashboard Purpose: Evaluate placement readiness across technical and behavioral matrices.\\n\\nFor queries, contact Admin:\\nEmail: placement@college.edu\\nPhone: +91-9876543210");
            },
            plugins: { legend: { display: false } }
        }
    });

    // 3. Donut Chart (Experience Matrix)
    let withInternship = 0, withCerts = 0, both = 0, neither = 0;
    students.forEach(s => {
        if(s.has_internship && s.has_cert) both++;
        else if(s.has_internship) withInternship++;
        else if(s.has_cert) withCerts++;
        else neither++;
    });

    const ctxDonut = document.getElementById('donutChart').getContext('2d');
    if(donutChart) donutChart.destroy();
    donutChart = new Chart(ctxDonut, {
        type: 'doughnut',
        data: {
            labels: ['Both', 'Internship Only', 'Cert Only', 'Neither'],
            datasets: [{
                data: [both, withInternship, withCerts, neither],
                backgroundColor: [
                    'rgba(153, 27, 27, 0.8)', // Dark Red
                    'rgba(220, 38, 38, 0.8)', // Primary Red
                    'rgba(248, 113, 113, 0.8)', // Light Red
                    'rgba(226, 232, 240, 0.8)'  // Gray
                ],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            onClick: (e, elements) => {
                alert("Dashboard Purpose: Evaluate placement readiness across technical and behavioral matrices.\\n\\nFor queries, contact Admin:\\nEmail: placement@college.edu\\nPhone: +91-9876543210");
            },
            plugins: {
                legend: { position: 'right', labels: { color: '#475569', font: {size: 11} } }
            },
            cutout: '75%'
        }
    });
}
        """)

    # js/app.js
    with open('js/app.js', 'w', encoding='utf-8') as f:
        f.write("""
window.allStudents = [];

document.addEventListener('DOMContentLoaded', async () => {
    try {
        if (window.location.protocol === 'file:') {
            throw new Error('FILE_PROTOCOL');
        }
        const response = await fetch('./data/students.json');
        if (!response.ok) throw new Error('Data fetch failed');
        window.allStudents = await response.json();
        
        setupFilters();
        renderDashboard(window.allStudents);
    } catch (err) {
        console.error(err);
        const tbody = document.getElementById('table-body');
        if (err.message === 'FILE_PROTOCOL') {
            tbody.innerHTML = `<tr><td colspan="7" class="text-center p-8">
                <div class="text-red-500 font-bold text-lg mb-2"><i class="fas fa-exclamation-triangle mr-2"></i>Security Restriction (CORS)</div>
                <div class="text-slate-600">You opened this file directly via <code>file:///</code>. Browsers block reading local JSON files for security.</div>
                <div class="text-slate-600 mt-2">Please run <code class="bg-red-50 px-2 py-1 rounded text-red-600 border border-red-200">python build_and_serve.py</code> and open <a href="http://localhost:8000" class="text-red-500 underline">http://localhost:8000</a></div>
            </td></tr>`;
        } else {
            tbody.innerHTML = `<tr><td colspan="7" class="text-center p-4 text-red-500 font-medium">Error loading data. Make sure the server is running.</td></tr>`;
        }
    }
});

function setupFilters() {
    const filters = ['search-input', 'cgpa-filter', 'backlog-filter', 'exp-filter'];
    filters.forEach(id => {
        document.getElementById(id).addEventListener('input', applyFilters);
    });
}

function applyFilters() {
    const search = document.getElementById('search-input').value.toLowerCase();
    const cgpaMin = parseFloat(document.getElementById('cgpa-filter').value) || 0;
    const backlogFilter = document.getElementById('backlog-filter').value;
    const expFilter = document.getElementById('exp-filter').value;

    const filtered = window.allStudents.filter(s => {
        const matchesSearch = s.name.toLowerCase().includes(search) || 
                              s.tech_stack.some(t => t.toLowerCase().includes(search)) ||
                              s.domains.some(d => d.toLowerCase().includes(search));
        
        const matchesCgpa = s.cgpa >= cgpaMin;
        
        let matchesBacklog = true;
        if(backlogFilter === '0') matchesBacklog = s.active_backlogs === 0;
        else if(backlogFilter === '>0') matchesBacklog = s.active_backlogs > 0;

        let matchesExp = true;
        if(expFilter === 'internship') matchesExp = s.has_internship;
        if(expFilter === 'cert') matchesExp = s.has_cert;
        if(expFilter === 'both') matchesExp = s.has_internship && s.has_cert;

        return matchesSearch && matchesCgpa && matchesBacklog && matchesExp;
    });

    renderDashboard(filtered);
}

function renderDashboard(data) {
    // KPIs
    document.getElementById('kpi-total').innerText = data.length;
    
    const avgScore = data.length ? (data.reduce((acc, s) => acc + s.portfolio_readiness, 0) / data.length).toFixed(1) : '0';
    document.getElementById('kpi-score').innerText = avgScore;
    
    const withExp = data.filter(s => s.has_internship || s.has_cert).length;
    const expPercent = data.length ? Math.round((withExp / data.length) * 100) : 0;
    document.getElementById('kpi-exp').innerText = `${expPercent}%`;
    
    const zeroBacklog = data.filter(s => s.active_backlogs === 0).length;
    document.getElementById('kpi-backlog').innerText = zeroBacklog;

    // Charts
    if(window.initCharts) initCharts(data);

    // Table
    const tbody = document.getElementById('table-body');
    tbody.innerHTML = '';
    
    if(data.length === 0) {
        tbody.innerHTML = `<tr><td colspan="7" class="text-center p-8 text-slate-400">No matching records found.</td></tr>`;
        return;
    }

    data.forEach((s, index) => {
        const tr = document.createElement('tr');
        tr.className = 'border-b border-slate-100 hover:bg-red-50/50 transition-colors cursor-pointer group';
        tr.onclick = (e) => {
            if(!e.target.closest('a')) openModal(s);
        };
        
        const stackBadges = s.tech_stack.slice(0, 3).map(t => `<span class="badge badge-purple mr-1 mb-1 inline-block">${t}</span>`).join('');
        const extraStack = s.tech_stack.length > 3 ? `<span class="badge bg-slate-100 text-slate-500 border border-slate-200 mr-1 mb-1 inline-block">+${s.tech_stack.length - 3}</span>` : '';
        
        let backlogBadge = s.active_backlogs === 0 
            ? `<span class="badge badge-green">Clear</span>`
            : `<span class="badge badge-red">Active</span>`;
            
        let expBadges = '';
        if(s.has_internship) expBadges += `<span class="badge badge-amber mr-1">Internship</span>`;
        if(s.has_cert) expBadges += `<span class="badge badge-blue mr-1">Cert</span>`;
        if(!s.has_internship && !s.has_cert) expBadges = `<span class="text-xs text-slate-400 font-medium">None</span>`;

        // Progress bar colors in light mode
        let color = s.portfolio_readiness >= 75 ? 'bg-red-600' : (s.portfolio_readiness >= 50 ? 'bg-red-400' : 'bg-red-200');

        tr.innerHTML = `
            <td class="p-3 font-semibold text-slate-800 group-hover:text-red-700 transition">${s.name}</td>
            <td class="p-3 text-red-600 font-bold">${s.cgpa.toFixed(2)}</td>
            <td class="p-3">${backlogBadge}</td>
            <td class="p-3">${expBadges}</td>
            <td class="p-3"><div class="flex flex-wrap">${stackBadges}${extraStack}</div></td>
            <td class="p-3">
                <div class="flex items-center gap-2">
                    <div class="w-full bg-slate-200 rounded-full h-2 border border-slate-300">
                      <div class="${color} h-2 rounded-full" style="width: ${s.portfolio_readiness}%"></div>
                    </div>
                    <span class="text-xs font-bold text-slate-700 w-8">${s.portfolio_readiness}</span>
                </div>
            </td>
            <td class="p-3 flex space-x-3 text-lg items-center h-full pt-4">
                ${s.github && s.github.length > 5 ? `<a href="${s.github}" target="_blank" class="text-slate-400 hover:text-red-600 transition"><i class="fab fa-github"></i></a>` : ''}
                ${s.linkedin && s.linkedin.length > 5 ? `<a href="${s.linkedin}" target="_blank" class="text-slate-400 hover:text-red-600 transition"><i class="fab fa-linkedin"></i></a>` : ''}
            </td>
        `;
        tbody.appendChild(tr);
    });
}

function openModal(s) {
    const modal = document.getElementById('student-modal');
    modal.classList.remove('hidden');
    
    document.getElementById('m-name').innerText = s.name;
    document.getElementById('m-cgpa').innerText = s.cgpa;
    document.getElementById('m-score').innerText = s.portfolio_readiness;
    
    const stack = s.tech_stack.map(t => `<span class="badge badge-purple mr-1 mb-1 inline-block">${t}</span>`).join('');
    document.getElementById('m-stack').innerHTML = stack || 'N/A';
    
    document.getElementById('m-intern').innerText = s.internship_details || 'None';
    document.getElementById('m-cert').innerText = s.cert_details || 'None';
    document.getElementById('m-self').innerText = s.self_learning || 'N/A';
    document.getElementById('m-comfort').innerText = s.comfort_level + '/5';
    document.getElementById('m-showcase').innerText = s.showcase || 'N/A';
    document.getElementById('m-adapt').innerText = s.adaptability || 'N/A';
    document.getElementById('m-time').innerText = s.time_spent || 'N/A';
    
    const links = document.getElementById('m-links');
    links.innerHTML = '';
    if(s.resume && s.resume.length > 5) links.innerHTML += `<a href="${s.resume}" target="_blank" class="px-3 py-1.5 bg-red-600 hover:bg-red-700 rounded-md text-xs font-semibold shadow-sm text-white transition"><i class="fas fa-file-pdf mr-1"></i>Resume</a>`;
    if(s.github && s.github.length > 5) links.innerHTML += `<a href="${s.github}" target="_blank" class="px-3 py-1.5 bg-slate-800 hover:bg-slate-900 rounded-md text-xs font-semibold shadow-sm text-white transition"><i class="fab fa-github mr-1"></i>GitHub</a>`;
    if(s.linkedin && s.linkedin.length > 5) links.innerHTML += `<a href="${s.linkedin}" target="_blank" class="px-3 py-1.5 bg-blue-700 hover:bg-blue-800 rounded-md text-xs font-semibold shadow-sm text-white transition"><i class="fab fa-linkedin mr-1"></i>LinkedIn</a>`;
    if(s.phone && s.phone.length > 5) links.innerHTML += `<a href="https://wa.me/${s.phone.replace(/[^0-9]/g, '')}" target="_blank" class="px-3 py-1.5 bg-emerald-600 hover:bg-emerald-700 rounded-md text-xs font-semibold shadow-sm text-white transition"><i class="fab fa-whatsapp mr-1"></i>${s.phone}</a>`;
    if(s.email && s.email.length > 5) links.innerHTML += `<a href="mailto:${s.email}" class="px-3 py-1.5 bg-rose-600 hover:bg-rose-700 rounded-md text-xs font-semibold shadow-sm text-white transition"><i class="fas fa-envelope mr-1"></i>Email</a>`;
}

window.openModal = openModal;

function closeModal() {
    document.getElementById('student-modal').classList.add('hidden');
}
        """)

    # index.html
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write("""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Marian MCA 2025-27 - Placement Portal</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link rel="stylesheet" href="css/style.css">
</head>
<body class="min-h-screen p-4 md:p-8 flex flex-col gap-6">

    <!-- Header -->
    <header class="flex flex-col md:flex-row justify-between items-center glass-panel rounded-2xl p-6">
        <div class="flex items-center gap-5">
            <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-red-500 to-red-700 flex items-center justify-center shadow-lg shadow-red-500/30">
                <i class="fas fa-graduation-cap text-white text-xl"></i>
            </div>
            <div>
                <h1 class="text-3xl font-extrabold text-slate-800 tracking-tight">Marian MCA 2025-27</h1>
                <p class="text-slate-500 text-sm font-medium mt-0.5">Placement Analytics Portal</p>
            </div>
        </div>
        <div class="mt-4 md:mt-0 flex gap-4">
            <button onclick="window.location.reload()" class="px-5 py-2.5 bg-white hover:bg-slate-50 text-slate-700 text-sm font-semibold rounded-xl border border-slate-200 shadow-sm transition flex items-center">
                <i class="fas fa-sync-alt mr-2 text-red-500"></i>Refresh Data
            </button>
        </div>
    </header>

    <!-- Info Banner -->
    <div class="glass-panel bg-red-50/50 rounded-2xl p-5 border-l-4 border-red-500 flex gap-4 items-start">
        <div class="text-red-500 text-xl mt-0.5"><i class="fas fa-info-circle"></i></div>
        <div>
            <h3 class="text-slate-800 font-bold text-sm uppercase tracking-wide">About This Portal</h3>
            <p class="text-slate-600 text-sm mt-1 leading-relaxed">
                This dashboard is exclusively designed for recruiters to discover, evaluate, and connect with the technical talent of the <strong>Marian MCA 2025-27</strong> batch. Use the matrices below to filter candidates by academic performance, real-world experience, and domain expertise. Click on any student to view their full profile, resume, and contact details.
            </p>
        </div>
    </div>

    <!-- KPIs -->
    <div class="grid grid-cols-2 lg:grid-cols-4 gap-5">
        <div class="glass-panel rounded-2xl p-6 relative overflow-hidden group">
            <div class="text-slate-500 text-xs font-bold uppercase tracking-wider mb-2">Total Candidates</div>
            <div class="text-4xl font-extrabold text-slate-800" id="kpi-total">-</div>
            <div class="absolute right-0 bottom-0 opacity-[0.03] group-hover:opacity-[0.06] transition-opacity transform translate-x-2 translate-y-2">
                <i class="fas fa-users text-7xl text-slate-900"></i>
            </div>
        </div>
        <div class="glass-panel rounded-2xl p-6 relative overflow-hidden group">
            <div class="text-slate-500 text-xs font-bold uppercase tracking-wider mb-2">Avg Readiness Score</div>
            <div class="text-4xl font-extrabold text-red-600" id="kpi-score">-</div>
            <div class="absolute right-0 bottom-0 opacity-[0.03] group-hover:opacity-[0.06] transition-opacity transform translate-x-2 translate-y-2">
                <i class="fas fa-tachometer-alt text-7xl text-red-900"></i>
            </div>
        </div>
        <div class="glass-panel rounded-2xl p-6 relative overflow-hidden group">
            <div class="text-slate-500 text-xs font-bold uppercase tracking-wider mb-2">Has Experience</div>
            <div class="text-4xl font-extrabold text-slate-800" id="kpi-exp">-</div>
            <div class="absolute right-0 bottom-0 opacity-[0.03] group-hover:opacity-[0.06] transition-opacity transform translate-x-2 translate-y-2">
                <i class="fas fa-briefcase text-7xl text-slate-900"></i>
            </div>
        </div>
        <div class="glass-panel rounded-2xl p-6 relative overflow-hidden group">
            <div class="text-slate-500 text-xs font-bold uppercase tracking-wider mb-2">Zero Backlogs</div>
            <div class="text-4xl font-extrabold text-green-600" id="kpi-backlog">-</div>
            <div class="absolute right-0 bottom-0 opacity-[0.03] group-hover:opacity-[0.06] transition-opacity transform translate-x-2 translate-y-2">
                <i class="fas fa-check-circle text-7xl text-green-900"></i>
            </div>
        </div>
    </div>

    <!-- Main Content Grid -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        <!-- Left Col: Charts -->
        <div class="lg:col-span-1 flex flex-col gap-6">
            <div class="glass-panel rounded-2xl p-6 flex-1 min-h-[300px]">
                <h2 class="text-sm font-bold text-slate-700 mb-5 uppercase tracking-wide">Readiness vs CGPA</h2>
                <div class="h-[220px]">
                    <canvas id="scatterChart"></canvas>
                </div>
            </div>
            <div class="grid grid-cols-2 gap-5">
                <div class="glass-panel rounded-2xl p-5">
                    <h2 class="text-xs font-bold text-slate-700 mb-3 uppercase tracking-wide text-center">Top Domains</h2>
                    <div class="h-[140px]">
                        <canvas id="radarChart"></canvas>
                    </div>
                </div>
                <div class="glass-panel rounded-2xl p-5">
                    <h2 class="text-xs font-bold text-slate-700 mb-3 uppercase tracking-wide text-center">Experience</h2>
                    <div class="h-[140px]">
                        <canvas id="donutChart"></canvas>
                    </div>
                </div>
            </div>
        </div>

        <!-- Right Col: Directory & Filters -->
        <div class="lg:col-span-2 glass-panel rounded-2xl flex flex-col overflow-hidden border border-slate-200">
            <!-- Filter Bar -->
            <div class="p-5 border-b border-slate-100 bg-white/50 flex flex-wrap gap-4 items-center">
                <div class="relative flex-1 min-w-[200px]">
                    <i class="fas fa-search absolute left-4 top-1/2 transform -translate-y-1/2 text-slate-400"></i>
                    <input type="text" id="search-input" placeholder="Search names, skills..." 
                        class="w-full bg-white border border-slate-200 text-sm font-medium rounded-xl pl-11 p-2.5 focus:ring-2 focus:ring-red-500 focus:border-red-500 text-slate-800 placeholder-slate-400 shadow-sm transition">
                </div>
                <select id="cgpa-filter" class="bg-white border border-slate-200 text-slate-700 font-medium text-sm rounded-xl p-2.5 focus:ring-2 focus:ring-red-500 shadow-sm outline-none cursor-pointer transition">
                    <option value="0">All CGPAs</option>
                    <option value="7">CGPA > 7.0</option>
                    <option value="8">CGPA > 8.0</option>
                    <option value="9">CGPA > 9.0</option>
                </select>
                <select id="exp-filter" class="bg-white border border-slate-200 text-slate-700 font-medium text-sm rounded-xl p-2.5 focus:ring-2 focus:ring-red-500 shadow-sm outline-none cursor-pointer transition">
                    <option value="all">All Experience</option>
                    <option value="internship">Has Internship</option>
                    <option value="cert">Has Certifications</option>
                    <option value="both">Internship + Certs</option>
                </select>
                <select id="backlog-filter" class="bg-white border border-slate-200 text-slate-700 font-medium text-sm rounded-xl p-2.5 focus:ring-2 focus:ring-red-500 shadow-sm outline-none cursor-pointer transition">
                    <option value="all">All Backlogs</option>
                    <option value="0">Zero Backlogs</option>
                    <option value=">0">Active Backlogs</option>
                </select>
            </div>
            
            <!-- Table -->
            <div class="p-0 table-container flex-1 bg-white/40">
                <table class="w-full text-sm text-left text-slate-600">
                    <thead class="text-xs uppercase font-bold text-slate-500 bg-slate-50 shadow-sm">
                        <tr>
                            <th class="px-5 py-4">Candidate</th>
                            <th class="px-5 py-4">CGPA</th>
                            <th class="px-5 py-4">Backlogs</th>
                            <th class="px-5 py-4">Experience</th>
                            <th class="px-5 py-4">Tech Stack</th>
                            <th class="px-5 py-4 w-48">Readiness Score</th>
                            <th class="px-5 py-4 text-center">Links</th>
                        </tr>
                    </thead>
                    <tbody id="table-body">
                        <!-- Rows rendered via JS -->
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    <!-- Modal Background -->
    <div id="student-modal" class="fixed inset-0 bg-slate-900/40 backdrop-blur-sm z-50 hidden flex items-center justify-center p-4">
        <!-- Modal Content -->
        <div class="glass-panel bg-white/95 rounded-2xl w-full max-w-3xl max-h-[90vh] overflow-y-auto flex flex-col shadow-2xl border border-slate-200">
            <div class="p-6 border-b border-slate-100 flex justify-between items-center bg-white/80 backdrop-blur-md sticky top-0 z-10">
                <div class="flex items-center gap-5">
                    <div class="w-14 h-14 rounded-full bg-red-50 flex items-center justify-center text-2xl font-bold text-red-600 shadow-inner border border-red-100">
                        <i class="fas fa-user-graduate"></i>
                    </div>
                    <div>
                        <h2 class="text-2xl font-extrabold text-slate-800" id="m-name">Student Name</h2>
                        <div class="flex gap-4 text-sm font-medium text-slate-500 mt-1">
                            <span><i class="fas fa-star text-red-500 mr-1.5"></i>Score: <strong class="text-red-600" id="m-score">-</strong>/100</span>
                            <span><i class="fas fa-graduation-cap text-slate-600 mr-1.5"></i>CGPA: <strong class="text-slate-800" id="m-cgpa">-</strong></span>
                        </div>
                    </div>
                </div>
                <button onclick="closeModal()" class="text-slate-400 hover:text-red-600 w-10 h-10 flex items-center justify-center rounded-full bg-slate-100 hover:bg-red-50 transition border border-transparent hover:border-red-200"><i class="fas fa-times"></i></button>
            </div>
            
            <div class="p-8 grid grid-cols-1 md:grid-cols-2 gap-8">
                <!-- Tech Stack & Links -->
                <div class="space-y-7">
                    <div>
                        <h3 class="text-xs font-bold text-slate-400 uppercase tracking-wider mb-3">Technical Arsenal</h3>
                        <div id="m-stack" class="flex flex-wrap gap-1.5"></div>
                    </div>
                    <div>
                        <h3 class="text-xs font-bold text-slate-400 uppercase tracking-wider mb-3">Profiles & Resume</h3>
                        <div id="m-links" class="flex gap-2.5 flex-wrap"></div>
                    </div>
                    <div class="bg-slate-50 rounded-xl p-5 border border-slate-100 shadow-sm">
                        <h3 class="text-xs font-bold text-slate-500 uppercase tracking-wider mb-2"><i class="fas fa-briefcase mr-1.5 text-red-500"></i>Internships</h3>
                        <p id="m-intern" class="text-sm font-medium text-slate-700"></p>
                    </div>
                    <div class="bg-slate-50 rounded-xl p-5 border border-slate-100 shadow-sm">
                        <h3 class="text-xs font-bold text-slate-500 uppercase tracking-wider mb-2"><i class="fas fa-certificate mr-1.5 text-amber-500"></i>Certifications</h3>
                        <p id="m-cert" class="text-sm font-medium text-slate-700"></p>
                    </div>
                </div>
                
                <!-- Behavioral Matrix -->
                <div class="space-y-4">
                    <div class="bg-slate-50 rounded-xl p-4 border border-slate-100 shadow-sm">
                        <h3 class="text-xs font-bold text-slate-500 uppercase tracking-wider mb-1.5">Self-Learning Drive</h3>
                        <p id="m-self" class="text-sm text-slate-800 font-semibold"></p>
                    </div>
                    <div class="bg-slate-50 rounded-xl p-4 border border-slate-100 shadow-sm">
                        <h3 class="text-xs font-bold text-slate-500 uppercase tracking-wider mb-1.5">Portfolio Showcase Readiness</h3>
                        <p id="m-showcase" class="text-sm text-slate-800 font-semibold"></p>
                    </div>
                    <div class="bg-slate-50 rounded-xl p-4 border border-slate-100 shadow-sm flex justify-between items-center">
                        <h3 class="text-xs font-bold text-slate-500 uppercase tracking-wider">Explanation Comfort</h3>
                        <span id="m-comfort" class="text-lg font-black text-red-600 bg-red-100 px-3 py-1 rounded-lg border border-red-200"></span>
                    </div>
                    <div class="bg-slate-50 rounded-xl p-4 border border-slate-100 shadow-sm">
                        <h3 class="text-xs font-bold text-slate-500 uppercase tracking-wider mb-1.5">Adaptability (Learn new stack)</h3>
                        <p id="m-adapt" class="text-sm text-slate-800 font-semibold"></p>
                    </div>
                    <div class="bg-slate-50 rounded-xl p-4 border border-slate-100 shadow-sm">
                        <h3 class="text-xs font-bold text-slate-500 uppercase tracking-wider mb-1.5">Time Spent Outside Curriculum</h3>
                        <p id="m-time" class="text-sm text-slate-800 font-semibold"></p>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="js/charts.js"></script>
    <script src="js/app.js"></script>
</body>
</html>
        """)

def serve(port=8000):
    Handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", port), Handler) as httpd:
        print(f"Serving at port {port}")
        threading.Thread(target=lambda: webbrowser.open(f'http://localhost:{port}/')).start()
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass
        httpd.server_close()

if __name__ == "__main__":
    ensure_dirs()
    sanitize_data()
    generate_static_files()
    
    try:
        serve()
    except OSError:
        print("Server already running on port 8000. Files updated.")
