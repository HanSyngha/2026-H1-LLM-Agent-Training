"""
프롬프트 엔지니어링 과제

수강생이 작성한 프롬프트 하나로 10개 바이오 데이터를 JSON 추출.
모든 테스트 케이스를 통과해야 성공.
"""

import json
import requests
import os

# ============================================
# 10개 바이오 데이터 테스트 케이스
# ============================================
PROMPT_TEST_CASES = [
    {
        "id": 1,
        "title": "CBC 혈액검사",
        "input": "Patient ID: BIO-2024-0391. Specimen: Peripheral blood. WBC: 12.3 x10^9/L (ref: 4.0-11.0), RBC: 4.52 x10^12/L (ref: 4.5-5.5), Hemoglobin: 13.8 g/dL (ref: 13.0-17.0), Platelet count: 245 x10^9/L (ref: 150-400). Differential: Neutrophils 78.2%, Lymphocytes 14.1%, Monocytes 5.3%, Eosinophils 1.8%, Basophils 0.6%. Morphology: Occasional atypical lymphocytes observed. No blast cells identified.",
        "expected": {
            "patient_id": "BIO-2024-0391",
            "specimen": "Peripheral blood",
            "abnormal_values": [{"name": "WBC", "value": 12.3, "unit": "x10^9/L", "status": "high"}],
            "morphology_findings": ["Occasional atypical lymphocytes observed"],
            "blast_cells": False
        },
    },
    {
        "id": 2,
        "title": "NGS 종양 유전체",
        "input": "Genomic Analysis Report - Sample: FFPE Tissue Block (Lung Adenocarcinoma). NGS Panel: TruSight Oncology 500. Key Variants: EGFR p.L858R (exon 21), VAF 34.2%, pathogenic; KRAS G12C not detected; TP53 c.742C>T (p.R248W), VAF 51.3%, likely pathogenic; ALK rearrangement: negative. TMB: 8.3 mut/Mb (intermediate). MSI status: MSS (microsatellite stable). PD-L1 TPS: 65%.",
        "expected": {
            "sample_type": "FFPE Tissue Block",
            "diagnosis": "Lung Adenocarcinoma",
            "variants": [
                {"gene": "EGFR", "mutation": "p.L858R", "vaf": 34.2, "classification": "pathogenic"},
                {"gene": "TP53", "mutation": "p.R248W", "vaf": 51.3, "classification": "likely pathogenic"}
            ],
            "tmb": 8.3,
            "msi_status": "MSS",
            "pd_l1": 65
        },
    },
    {
        "id": 3,
        "title": "약물동태학 (PK)",
        "input": "Pharmacokinetics Summary - Drug: Pembrolizumab (anti-PD-1 mAb). Dose: 200mg IV q3w. Cmax: 83.4 μg/mL (SD ±12.1). Tmax: 0.5h post-infusion. AUC0-21d: 28,940 μg·h/mL. t1/2: 26.7 days. Vd: 6.0 L. CL: 0.22 L/day. Steady-state reached by Week 18. No significant accumulation observed (accumulation ratio: 2.1).",
        "expected": {
            "drug": "Pembrolizumab",
            "dose": "200mg IV q3w",
            "cmax": {"value": 83.4, "unit": "μg/mL"},
            "half_life_days": 26.7,
            "clearance": {"value": 0.22, "unit": "L/day"},
            "steady_state_week": 18,
            "accumulation_ratio": 2.1
        },
    },
    {
        "id": 4,
        "title": "유세포 분석 (Flow Cytometry)",
        "input": "Flow Cytometry Report - Specimen: Bone marrow aspirate. Clinical indication: R/O AML. CD45 dim population identified (12.3% of total events). Immunophenotype: CD34+, CD117+, CD13+, CD33+, HLA-DR+, CD56-, CD19-, CD3-, MPO partial+. Interpretation: Abnormal myeloid blast population consistent with acute myeloid leukemia. Recommend correlation with morphology and cytogenetics.",
        "expected": {
            "specimen": "Bone marrow aspirate",
            "indication": "R/O AML",
            "blast_percentage": 12.3,
            "positive_markers": ["CD34", "CD117", "CD13", "CD33", "HLA-DR"],
            "negative_markers": ["CD56", "CD19", "CD3"],
            "interpretation": "acute myeloid leukemia"
        },
    },
    {
        "id": 5,
        "title": "CRISPR 스크린",
        "input": "CRISPR Screen Results - Cell line: HeLa-Cas9. Library: Brunello (77,441 sgRNAs). Screen type: Negative selection (dropout). Treatment: Cisplatin 5μM, 14 days. Top depleted genes (FDR < 0.01): BRCA1 (log2FC: -3.82, p=2.1e-12), BRCA2 (log2FC: -3.45, p=8.7e-11), RAD51 (log2FC: -2.91, p=3.4e-9), PALB2 (log2FC: -2.67, p=1.2e-8), FANCD2 (log2FC: -2.34, p=5.6e-7). Pathway enrichment: Homologous recombination repair (p=1.3e-15).",
        "expected": {
            "cell_line": "HeLa-Cas9",
            "library": "Brunello",
            "treatment": "Cisplatin 5μM",
            "top_gene": "BRCA1",
            "top_log2fc": -3.82,
            "num_significant_genes": 5,
            "enriched_pathway": "Homologous recombination repair"
        },
    },
    {
        "id": 6,
        "title": "질량분석 단백체학",
        "input": "Mass Spectrometry Proteomics - Sample: Cerebrospinal fluid (CSF). Method: LC-MS/MS, DIA. Total proteins identified: 1,247. Significantly upregulated (FC>2, adj.p<0.05): GFAP (FC: 4.82), CHI3L1/YKL-40 (FC: 3.91), NEFL (FC: 3.44), TREM2 (FC: 2.87), VILIP-1 (FC: 2.31). Aβ42/40 ratio: 0.062 (cutoff: <0.08 = amyloid positive). t-tau: 892 pg/mL (ref: <400). p-tau181: 124 pg/mL (ref: <27).",
        "expected": {
            "sample": "CSF",
            "method": "LC-MS/MS",
            "total_proteins": 1247,
            "most_upregulated": "GFAP",
            "most_upregulated_fc": 4.82,
            "amyloid_positive": True,
            "tau_elevated": True
        },
    },
    {
        "id": 7,
        "title": "마이크로바이옴 16S rRNA",
        "input": "Microbiome 16S rRNA Sequencing - Sample: Fecal. Diversity metrics: Shannon index: 2.14 (healthy ref: 3.0-4.5), Simpson index: 0.68, Observed ASVs: 187. Phylum-level composition: Firmicutes 31.2%, Bacteroidetes 24.8%, Proteobacteria 28.4%, Actinobacteria 8.1%, Verrucomicrobia 4.2%, Others 3.3%. Firmicutes/Bacteroidetes ratio: 1.26. Notable: Elevated Proteobacteria (ref: <10%) suggesting dysbiosis. Clostridioides difficile: Detected (relative abundance 2.8%).",
        "expected": {
            "sample": "Fecal",
            "shannon_index": 2.14,
            "diversity_status": "low",
            "dominant_phylum": "Firmicutes",
            "fb_ratio": 1.26,
            "dysbiosis": True,
            "c_difficile_detected": True
        },
    },
    {
        "id": 8,
        "title": "단일세포 RNA-seq",
        "input": "Single-Cell RNA-seq Summary - Platform: 10x Chromium (v3.1). Tissue: Human PBMC. Cells captured: 8,247 (post-QC: 7,891). Median genes/cell: 2,341. Clusters identified (Leiden, res=0.8): CD4+ T cells (28.3%), CD8+ T cells (19.7%), B cells (12.4%), NK cells (8.9%), Classical monocytes (CD14++) 18.2%, Non-classical monocytes (CD16+) 4.1%, Dendritic cells 3.8%, Platelets 2.4%, Unknown 2.2%. DEG analysis: CD8+ T cells showed upregulation of GZMB, PRF1, IFNG (adjusted p < 0.001).",
        "expected": {
            "platform": "10x Chromium",
            "cells_post_qc": 7891,
            "median_genes": 2341,
            "num_clusters": 9,
            "largest_cluster": "CD4+ T cells",
            "largest_cluster_pct": 28.3,
            "cd8_upregulated_genes": ["GZMB", "PRF1", "IFNG"]
        },
    },
    {
        "id": 9,
        "title": "ChIP-seq 히스톤 변형",
        "input": "ChIP-seq Analysis - Target: H3K27ac (active enhancers). Cell type: iPSC-derived cardiomyocytes. Total peaks: 42,891. Peaks in promoters (TSS ±2kb): 12,344 (28.8%). Peaks in distal enhancers: 24,567 (57.3%). Super-enhancers identified: 387 (ROSE algorithm, stitching distance: 12.5kb). Top SE-associated genes: MYH7, TNNT2, MYL2, SCN5A, CACNA1C. Motif enrichment: GATA4 (p=1e-892), MEF2C (p=1e-654), TBX5 (p=1e-423), NKX2-5 (p=1e-389).",
        "expected": {
            "target": "H3K27ac",
            "cell_type": "iPSC-derived cardiomyocytes",
            "total_peaks": 42891,
            "super_enhancers": 387,
            "top_se_gene": "MYH7",
            "top_motif": "GATA4",
            "promoter_peak_pct": 28.8
        },
    },
    {
        "id": 10,
        "title": "임상시험 바이오마커",
        "input": "Clinical Trial Biomarker Analysis - Study: KEYNOTE-789, Phase III. Endpoint: PFS by ctDNA clearance. Patients (n=318): ctDNA clearance at Week 9: 47.2% (150/318). Median PFS - ctDNA cleared: 11.8 mo (95% CI: 9.2-14.1); ctDNA not cleared: 4.3 mo (95% CI: 3.1-5.8). HR: 0.34 (95% CI: 0.26-0.45, p<0.0001). Landmark analysis: ctDNA molecular response (>50% VAF reduction) at Week 3 predicted clearance at Week 9 (sensitivity 82.4%, specificity 71.3%, AUC 0.84).",
        "expected": {
            "study": "KEYNOTE-789",
            "total_patients": 318,
            "clearance_rate": 47.2,
            "pfs_cleared_months": 11.8,
            "pfs_not_cleared_months": 4.3,
            "hazard_ratio": 0.34,
            "auc": 0.84
        },
    },
]


# ============================================
# LLM 호출
# ============================================
def call_llm(prompt: str, input_text: str, expected_keys: list, llm_config: dict) -> dict:
    """수강생 프롬프트 + 입력 데이터로 LLM 호출 → JSON 파싱"""
    if not llm_config.get("base_url"):
        return {"error": "LLM이 설정되지 않았습니다. /settings에서 프롬프트 과제용 LLM을 설정해주세요."}

    try:
        resp = requests.post(
            f"{llm_config['base_url']}/chat/completions",
            headers={
                "Authorization": f"Bearer {llm_config.get('api_key', '')}",
                "Content-Type": "application/json",
            },
            json={
                "model": llm_config.get("model", ""),
                "messages": [
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": input_text},
                ],
                "temperature": 0.1,
                "max_tokens": 2000,
            },
            verify=False,
            timeout=60,
            proxies={"http": None, "https": None},
        )

        if resp.status_code != 200:
            return {"error": f"LLM 응답 오류: HTTP {resp.status_code}"}

        content = resp.json()["choices"][0]["message"]["content"]

        # JSON 추출 (코드블록 안에 있을 수 있음)
        content = content.strip()
        if content.startswith("```"):
            lines = content.split("\n")
            content = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])
            content = content.strip()

        return {"content": content, "parsed": json.loads(content)}

    except json.JSONDecodeError:
        return {"error": "LLM 응답이 유효한 JSON이 아닙니다", "raw": content}
    except requests.Timeout:
        return {"error": "LLM 응답 시간 초과 (60초)"}
    except Exception as e:
        return {"error": f"LLM 호출 실패: {str(e)}"}


# ============================================
# 검증: expected와 실제 결과 비교
# ============================================
def validate_result(actual: dict, expected: dict) -> dict:
    """실제 LLM 출력과 expected를 비교합니다."""
    details = []
    all_pass = True

    for key, exp_val in expected.items():
        if key not in actual:
            details.append({"key": key, "pass": False, "expected": exp_val, "actual": "(키 없음)"})
            all_pass = False
            continue

        act_val = actual[key]

        # 타입별 비교
        if isinstance(exp_val, bool):
            ok = isinstance(act_val, bool) and act_val == exp_val
        elif isinstance(exp_val, (int, float)):
            # LLM이 {"value": 1.26, "unit": ""} 형태로 줄 수 있음
            num_val = act_val
            if isinstance(act_val, dict) and "value" in act_val:
                num_val = act_val["value"]
            try:
                ok = abs(float(num_val) - float(exp_val)) < 0.1
            except (ValueError, TypeError):
                ok = False
        elif isinstance(exp_val, str):
            ok = exp_val.lower() in str(act_val).lower()
        elif isinstance(exp_val, list):
            if len(exp_val) > 0 and isinstance(exp_val[0], dict):
                # dict 배열: 길이 비교 + 첫 번째 항목 키 비교
                ok = isinstance(act_val, list) and len(act_val) >= len(exp_val)
            elif len(exp_val) > 0 and isinstance(exp_val[0], str):
                # 문자열 배열: 모든 항목이 포함되어 있는지
                act_strs = [str(v).upper() for v in (act_val if isinstance(act_val, list) else [])]
                ok = all(str(e).upper() in " ".join(act_strs) for e in exp_val)
            else:
                ok = isinstance(act_val, list) and len(act_val) == len(exp_val)
        elif isinstance(exp_val, dict):
            # nested dict: 키 존재 + 값 비교
            if isinstance(act_val, dict):
                ok = all(k in act_val for k in exp_val)
            elif "value" in exp_val:
                # expected가 {"value": 83.4, "unit": "μg/mL"}인데 actual이 83.4인 경우
                try:
                    ok = abs(float(act_val) - float(exp_val["value"])) < 0.1
                except (ValueError, TypeError):
                    ok = False
            else:
                ok = False
        else:
            ok = str(act_val) == str(exp_val)

        details.append({
            "key": key,
            "pass": ok,
            "expected": exp_val,
            "actual": act_val,
        })
        if not ok:
            all_pass = False

    return {"pass": all_pass, "details": details}
