
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
        