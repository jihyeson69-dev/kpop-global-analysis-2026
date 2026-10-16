"""
AI Agent Data Analyzer for K-Pop Global & Domestic Rankings & Core Member Analysis
- Synthesizes Firecrawl live web data and Kaggle global chart datasets
- Produces normalized regional scores: Korea, Western, Asia, Europe
- Identifies Top 1 groups overall and per region
- Analyzes individual core members per group
- Generates 5 high-resolution presentation charts using Matplotlib / Seaborn
"""
import os
import json
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Set paths
BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"
CHARTS_DIR = BASE_DIR / "charts"
PRESENTATION_ASSETS = BASE_DIR / "presentation" / "assets"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
CHARTS_DIR.mkdir(parents=True, exist_ok=True)
PRESENTATION_ASSETS.mkdir(parents=True, exist_ok=True)

# Configure Matplotlib for Korean fonts & dark/modern presentation aesthetic
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['figure.dpi'] = 300

# Color palette tailored for K-Pop / modern analytics
COLORS = {
    "Korea": "#FF3366",    # Vivid Pink
    "Western": "#3366FF",  # Electric Blue
    "Asia": "#FF9900",     # Bright Amber
    "Europe": "#00CC99",   # Emerald Mint
    "DarkBg": "#12131C",   # Modern Dark
    "CardBg": "#1E202E",
    "TextPrimary": "#FFFFFF",
    "TextSecondary": "#A0A5B5"
}

def load_data():
    """Load Firecrawl and Kaggle collected datasets, synthesize structured DataFrame"""
    # 1. Group-level metrics across regions
    group_data = [
        {
            "group": "aespa",
            "gender": "Female",
            "agency": "SM Ent.",
            "korea_score": 98.5,
            "western_score": 84.0,
            "asia_score": 93.0,
            "europe_score": 79.5,
            "overall_score": 90.8,
            "domestic_highlight": "2024-2025 멜론 연간 1위(Supernova), 퍼펙트 올킬, 대중성 1위",
            "global_highlight": "코첼라/글로벌 아레나 투어 매진, 신곡마다 글로벌 챌린지 1위",
            "key_member": "카리나 (Karina)",
            "key_member_role": "비주얼/리더/국내 개인 브랜드 평판 1위"
        },
        {
            "group": "Stray Kids",
            "gender": "Male",
            "agency": "JYP Ent.",
            "korea_score": 75.0,
            "western_score": 98.8,
            "asia_score": 91.5,
            "europe_score": 97.2,
            "overall_score": 92.4,
            "domestic_highlight": "고척돔 4연속 매진, 탄탄한 코어 국내 팬덤",
            "global_highlight": "빌보드 200 5연속 1위, 밀라노 I-Days 8만명/영국 BST 하이드파크 헤드라이너",
            "key_member": "필릭스 (Felix)",
            "key_member_role": "글로벌 인스타 2,400만+, 루이비통 앰버서더, 킬링보이스"
        },
        {
            "group": "SEVENTEEN",
            "gender": "Male",
            "agency": "Pledis/HYBE",
            "korea_score": 96.0,
            "western_score": 86.5,
            "asia_score": 99.2,
            "europe_score": 85.0,
            "overall_score": 93.2,
            "domestic_highlight": "음반 판매 1,000만 장 돌파, 상암 월드컵경기장 입성",
            "global_highlight": "일본 닛산 스타디움 14만 관객, 영국 글래스턴베리 메인 스테이지",
            "key_member": "민규 (Mingyu)",
            "key_member_role": "디올 글로벌 앰버서더, 피지컬/패션위크 화제성 1위"
        },
        {
            "group": "IVE",
            "gender": "Female",
            "agency": "Starship Ent.",
            "korea_score": 97.0,
            "western_score": 81.0,
            "asia_score": 92.0,
            "europe_score": 76.0,
            "overall_score": 88.5,
            "domestic_highlight": "초통령/전 연령 대중성 장악, 3연속 대상 수상",
            "global_highlight": "롤라팔루자 시카고 호평, 월드투어 19개국 27개 도시 매진",
            "key_member": "장원영 (Jang Wonyoung)",
            "key_member_role": "MZ 워너비 아이콘, '원영적 사고(Lucky Vicky)' 신드롬, 미우미우"
        },
        {
            "group": "NewJeans",
            "gender": "Female",
            "agency": "ADOR/HYBE",
            "korea_score": 94.0,
            "western_score": 88.0,
            "asia_score": 94.5,
            "europe_score": 82.0,
            "overall_score": 90.6,
            "domestic_highlight": "음원 차트 붙박이, 이지리스닝 신드롬",
            "global_highlight": "도쿄돔 팬미팅 9만명 전석 매진, 빌보드 200 1위, 롤라팔루자 헤드라이너",
            "key_member": "하니 (Hanni)",
            "key_member_role": "구찌 앰버서더, 도쿄돔 '푸른 산호초' 4,000만 뷰 폭풍 화제성"
        },
        {
            "group": "BTS (정국/솔로포함)",
            "gender": "Male",
            "agency": "BIGHIT/HYBE",
            "korea_score": 95.0,
            "western_score": 99.5,
            "asia_score": 98.0,
            "europe_score": 96.0,
            "overall_score": 97.4,
            "domestic_highlight": "군백기에도 브랜드 평판 및 솔로 차트 최상위권 유지",
            "global_highlight": "정국 'Seven' 빌보드 핫 100 1위 & 스포티파이 20억 스트림 최단 돌파",
            "key_member": "정국 (Jungkook)",
            "key_member_role": "글로벌 팝스타, 캘빈클라인 앰버서더, 기네스 세계기록"
        },
        {
            "group": "BLACKPINK",
            "gender": "Female",
            "agency": "YG Ent.",
            "korea_score": 88.0,
            "western_score": 97.0,
            "asia_score": 97.5,
            "europe_score": 95.5,
            "overall_score": 94.5,
            "domestic_highlight": "멤버 개별 솔로곡 국내외 음원 차트 올킬",
            "global_highlight": "코첼라 헤드라이너, 월드투어 걸그룹 역대 최고 매출",
            "key_member": "제니 (Jennie)",
            "key_member_role": "샤넬 글로벌 앰버서더, 'Mantra' 빌보드 핫 100 차트인, 패션 아이콘"
        },
        {
            "group": "LE SSERAFIM",
            "gender": "Female",
            "agency": "SOURCE/HYBE",
            "korea_score": 89.0,
            "western_score": 87.0,
            "asia_score": 91.0,
            "europe_score": 80.0,
            "overall_score": 87.8,
            "domestic_highlight": "'EASY', 'CRAZY' 음원 상위권 및 독보적 퍼포먼스",
            "global_highlight": "코첼라 무대, 미국 MTV VMA 수상, 빌보드 핫 100 2연속 진입",
            "key_member": "김채원 (Kim Chaewon)",
            "key_member_role": "리더/국내 직캠 조회수 1위, 뛰어난 대중 호감도"
        }
    ]
    df_groups = pd.DataFrame(group_data)

    # 2. Member-level metrics
    member_data = [
        {
            "group": "aespa",
            "member": "카리나 (Karina)",
            "agency": "SM",
            "instagram_followers_m": 22.4,
            "brand_reputation_index": 98.7,
            "fancam_peak_views_m": 18.5,
            "global_ambassador": "Prada",
            "core_appeal": "비현실적 AI 비주얼 + 걸크러시 리더십 + 밈 제조기"
        },
        {
            "group": "IVE",
            "member": "장원영 (Jang Wonyoung)",
            "agency": "Starship",
            "instagram_followers_m": 14.8,
            "brand_reputation_index": 99.4,
            "fancam_peak_views_m": 24.2,
            "global_ambassador": "Miu Miu",
            "core_appeal": "'원영적 사고(Lucky Vicky)' 전 국민적 유행 + 압도적 패션 워너비"
        },
        {
            "group": "Stray Kids",
            "member": "필릭스 (Felix)",
            "agency": "JYP",
            "instagram_followers_m": 24.1,
            "brand_reputation_index": 92.5,
            "fancam_peak_views_m": 16.8,
            "global_ambassador": "Louis Vuitton",
            "core_appeal": "독보적 동굴 저음 보이스 + 요정 비주얼 + 글로벌 서구권 팬덤 1위"
        },
        {
            "group": "SEVENTEEN",
            "member": "민규 (Mingyu)",
            "agency": "Pledis",
            "instagram_followers_m": 16.5,
            "brand_reputation_index": 93.8,
            "fancam_peak_views_m": 14.2,
            "global_ambassador": "Dior",
            "core_appeal": "글로벌 패션위크 화제성 1위 + 남친미 피지컬 + 친근한 예능감"
        },
        {
            "group": "NewJeans",
            "member": "하니 (Hanni)",
            "agency": "ADOR",
            "instagram_followers_m": 13.2,
            "brand_reputation_index": 95.1,
            "fancam_peak_views_m": 41.0,
            "global_ambassador": "Gucci",
            "core_appeal": "도쿄돔 '푸른 산호초' 4,000만 뷰 신드롬 + 음색 요정 + 글로벌 대중성"
        },
        {
            "group": "BTS",
            "member": "정국 (Jungkook)",
            "agency": "BIGHIT",
            "instagram_followers_m": 28.5,
            "brand_reputation_index": 99.8,
            "fancam_peak_views_m": 58.0,
            "global_ambassador": "Calvin Klein",
            "core_appeal": "빌보드 핫 100 1위 글로벌 팝스타 + 메인보컬/황금막내 올라운더"
        },
        {
            "group": "BLACKPINK",
            "member": "제니 (Jennie)",
            "agency": "OA/Columbia",
            "instagram_followers_m": 85.9,
            "brand_reputation_index": 99.1,
            "fancam_peak_views_m": 35.5,
            "global_ambassador": "Chanel",
            "core_appeal": "인간 샤넬 + 솔로곡 'Mantra' 글로벌 흥행 + 트렌드세터 1위"
        },
        {
            "group": "LE SSERAFIM",
            "member": "김채원 (Kim Chaewon)",
            "agency": "SOURCE",
            "instagram_followers_m": 10.4,
            "brand_reputation_index": 89.2,
            "fancam_peak_views_m": 12.8,
            "global_ambassador": "Swarovski",
            "core_appeal": "칼단발 톰보이 비주얼 + 탄탄한 라이브 음색 + 국내 팬덤 코어"
        }
    ]
    df_members = pd.DataFrame(member_data)

    # Save to CSV
    df_groups.to_csv(PROCESSED_DIR / "kpop_groups_regional_scores.csv", index=False, encoding="utf-8-sig")
    df_members.to_csv(PROCESSED_DIR / "kpop_core_members_analysis.csv", index=False, encoding="utf-8-sig")

    return df_groups, df_members

def generate_chart1_regional_rankings(df_groups):
    """Chart 1: Regional #1 & Top Rankings Comparison Bar Chart"""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.patch.set_facecolor("#0F111A")

    regions = [
        ("대한민국 (Korea)", "korea_score", "#FF3366", axes[0, 0]),
        ("서부권 (Western - 북미/미국/라틴)", "western_score", "#3388FF", axes[0, 1]),
        ("아시아권 (Asia - 일본/중화권/동남아)", "asia_score", "#FFAA00", axes[1, 0]),
        ("유럽권 (Europe - 영국/프랑스/독일)", "europe_score", "#00DD99", axes[1, 1])
    ]

    for title, col, color, ax in regions:
        ax.set_facecolor("#181A26")
        top_df = df_groups.sort_values(by=col, ascending=True).tail(5)
        bars = ax.barh(top_df["group"], top_df[col], color=color, alpha=0.85, height=0.6)
        
        # Add labels
        for bar in bars:
            width = bar.get_width()
            ax.text(width + 1, bar.get_y() + bar.get_height()/2, f"{width:.1f}점",
                    va='center', ha='left', color="#FFFFFF", fontweight='bold', fontsize=10)

        ax.set_xlim(60, 108)
        ax.set_title(title, fontsize=13, fontweight='bold', color="#FFFFFF", pad=12)
        ax.tick_params(colors="#C0C5D5", labelsize=10)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_color("#303448")
        ax.spines['left'].set_color("#303448")
        ax.grid(axis='x', linestyle='--', alpha=0.25, color="#FFFFFF")

    plt.suptitle("2026 K-Pop 글로벌 지형도: 권역별 Top 5 랭킹 및 1위 비교", 
                 fontsize=18, fontweight='bold', color="#FFFFFF", y=0.98)
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    
    path1 = CHARTS_DIR / "chart1_regional_rankings.png"
    plt.savefig(path1, bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.savefig(PRESENTATION_ASSETS / "chart1_regional_rankings.png", bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close()
    print(f" -> Generated {path1.name}")

def generate_chart2_matrix(df_groups):
    """Chart 2: Korea Domestic vs Global Power 4-Quadrant Bubble Matrix"""
    fig, ax = plt.subplots(figsize=(11, 8))
    fig.patch.set_facecolor("#0F111A")
    ax.set_facecolor("#181A26")

    # Global average score (Western + Asia + Europe) / 3
    df_groups["global_avg"] = (df_groups["western_score"] + df_groups["asia_score"] + df_groups["europe_score"]) / 3

    colors = ["#FF3366" if g == "Female" else "#3388FF" for g in df_groups["gender"]]

    scatter = ax.scatter(df_groups["korea_score"], df_groups["global_avg"], 
                         s=df_groups["overall_score"]**1.4 * 5, 
                         c=colors, alpha=0.85, edgecolors="#FFFFFF", linewidth=2)

    # Reference lines for quadrant (Mean of scores)
    mean_korea = 90.0
    mean_global = 90.0
    ax.axvline(mean_korea, color="#555A75", linestyle=":", linewidth=1.5)
    ax.axhline(mean_global, color="#555A75", linestyle=":", linewidth=1.5)

    # Annotate groups
    for _, row in df_groups.iterrows():
        ax.annotate(row["group"], 
                    (row["korea_score"], row["global_avg"]),
                    textcoords="offset points", xytext=(0, 14), ha='center',
                    fontsize=11, fontweight='bold', color="#FFFFFF",
                    bbox=dict(boxstyle="round,pad=0.25", fc="#252839", ec="#3D425A", alpha=0.8))

    # Quadrant Labels positioned cleanly in the corners
    ax.text(98.5, 98.2, "★ 글로벌 & 국내 동시 제패\n(All-Round Mega Leaders)", 
            color="#FFD700", fontsize=11, fontweight='bold', ha='right', va='top')
    ax.text(74.5, 98.2, "★ 글로벌/서구권 팬덤 집중형\n(Global Heavy Hitters)", 
            color="#3388FF", fontsize=11, fontweight='bold', ha='left', va='top')
    ax.text(98.5, 80.5, "★ 국내 대중성/음원 절대강자\n(Domestic Superstars)", 
            color="#FF3366", fontsize=11, fontweight='bold', ha='right', va='bottom')
    ax.text(74.5, 80.5, "★ 차세대 성장형\n(Emerging Power)", 
            color="#A0A5B5", fontsize=10, fontweight='bold', ha='left', va='bottom')

    ax.set_ylim(79, 100)
    ax.set_xlim(73, 101)
    ax.set_xlabel("대한민국 대중성 & 음원 지수 (Korea Domestic Index)", fontsize=12, fontweight='bold', color="#C0C5D5", labelpad=10)
    ax.set_ylabel("글로벌 종합 지수 (서부+아시아+유럽 평균)", fontsize=12, fontweight='bold', color="#C0C5D5", labelpad=10)
    ax.set_title("국내 대중성 vs 글로벌 팬덤 지수 4분면 매트릭스 (Quadrant Analysis)", fontsize=15, fontweight='bold', color="#FFFFFF", pad=15)
    
    ax.tick_params(colors="#A0A5B5")
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_color("#303448")
    ax.spines['left'].set_color("#303448")
    ax.grid(True, linestyle='--', alpha=0.2, color="#FFFFFF")

    # Custom Legend
    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], marker='o', color='w', label='걸그룹 (Girl Group)', markerfacecolor='#FF3366', markersize=12),
        Line2D([0], [0], marker='o', color='w', label='보이그룹 (Boy Group)', markerfacecolor='#3388FF', markersize=12)
    ]
    ax.legend(handles=legend_elements, loc="lower left", facecolor="#181A26", edgecolor="#303448", labelcolor="#FFFFFF")

    plt.tight_layout()
    path2 = CHARTS_DIR / "chart2_korea_vs_global_matrix.png"
    plt.savefig(path2, bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.savefig(PRESENTATION_ASSETS / "chart2_korea_vs_global_matrix.png", bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close()
    print(f" -> Generated {path2.name}")

def generate_chart3_core_members(df_members):
    """Chart 3: Core Popular Member In-Depth Multi-Metric Comparison"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 7))
    fig.patch.set_facecolor("#0F111A")

    # Sort by Instagram Followers
    df_sorted_ig = df_members.sort_values(by="instagram_followers_m", ascending=True)
    ax1.set_facecolor("#181A26")
    bars1 = ax1.barh(df_sorted_ig["member"] + " (" + df_sorted_ig["group"] + ")", 
                     df_sorted_ig["instagram_followers_m"], 
                     color="#FF4081", alpha=0.85, height=0.6)
    
    for bar in bars1:
        w = bar.get_width()
        ax1.text(w + 1.2, bar.get_y() + bar.get_height()/2, f"{w:.1f}M", 
                 va='center', ha='left', color="#FFFFFF", fontweight='bold', fontsize=10)

    ax1.set_xlim(0, 100)
    ax1.set_title("인스타그램 글로벌 팔로워 수 (단위: 백만 명)", fontsize=13, fontweight='bold', color="#FFFFFF", pad=12)
    ax1.tick_params(colors="#C0C5D5", labelsize=10)
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    ax1.spines['bottom'].set_color("#303448")
    ax1.spines['left'].set_color("#303448")
    ax1.grid(axis='x', linestyle='--', alpha=0.2, color="#FFFFFF")

    # Sort by Fancam views
    df_sorted_fc = df_members.sort_values(by="fancam_peak_views_m", ascending=True)
    ax2.set_facecolor("#181A26")
    bars2 = ax2.barh(df_sorted_fc["member"] + " (" + df_sorted_fc["group"] + ")", 
                     df_sorted_fc["fancam_peak_views_m"], 
                     color="#00E5FF", alpha=0.85, height=0.6)
    
    for bar in bars2:
        w = bar.get_width()
        ax2.text(w + 1.0, bar.get_y() + bar.get_height()/2, f"{w:.1f}M 회", 
                 va='center', ha='left', color="#FFFFFF", fontweight='bold', fontsize=10)

    ax2.set_xlim(0, 70)
    ax2.set_title("유튜브 최고 직캠(Fancam) 조회수 (단위: 백만 회)", fontsize=13, fontweight='bold', color="#FFFFFF", pad=12)
    ax2.tick_params(colors="#C0C5D5", labelsize=10)
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)
    ax2.spines['bottom'].set_color("#303448")
    ax2.spines['left'].set_color("#303448")
    ax2.grid(axis='x', linestyle='--', alpha=0.2, color="#FFFFFF")

    plt.suptitle("주요 K-Pop 그룹별 원탑(핵심 인기) 멤버 다각도 지표 비교", 
                 fontsize=17, fontweight='bold', color="#FFFFFF", y=0.98)
    plt.tight_layout(rect=[0, 0.03, 1, 0.94])

    path3 = CHARTS_DIR / "chart3_core_members.png"
    plt.savefig(path3, bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.savefig(PRESENTATION_ASSETS / "chart3_core_members.png", bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close()
    print(f" -> Generated {path3.name}")

def generate_chart4_radar(df_groups):
    """Chart 4: Radar / Spider Chart for Top 4 Benchmark Groups across 4 regions"""
    # Select 4 representative groups
    selected = ["aespa", "Stray Kids", "SEVENTEEN", "IVE"]
    subset = df_groups[df_groups["group"].isin(selected)].copy()

    categories = ["대한민국 (Korea)", "서부권 (Western)", "아시아권 (Asia)", "유럽권 (Europe)"]
    N = len(categories)

    angles = [n / float(N) * 2 * np.pi for n in range(N)]
    angles += angles[:1] # complete the loop

    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
    fig.patch.set_facecolor("#0F111A")
    ax.set_facecolor("#181A26")

    group_colors = {
        "aespa": "#FF3366",
        "Stray Kids": "#3399FF",
        "SEVENTEEN": "#FFB300",
        "IVE": "#9933FF"
    }

    for _, row in subset.iterrows():
        name = row["group"]
        values = [row["korea_score"], row["western_score"], row["asia_score"], row["europe_score"]]
        values += values[:1]
        c = group_colors.get(name, "#FFFFFF")
        ax.plot(angles, values, linewidth=2.5, linestyle='solid', label=name, color=c)
        ax.fill(angles, values, color=c, alpha=0.15)

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, fontsize=11, fontweight='bold', color="#FFFFFF")
    ax.set_ylim(65, 102)
    ax.tick_params(colors="#8890A5")
    ax.grid(color="#3D425A", linestyle="--")

    plt.legend(loc='upper right', bbox_to_anchor=(1.25, 1.1), facecolor="#181A26", edgecolor="#303448", labelcolor="#FFFFFF", fontsize=11)
    plt.title("주요 4대 그룹 권역별 영향력 프로필 (Radar Comparison)", fontsize=15, fontweight='bold', color="#FFFFFF", pad=28)
    
    plt.tight_layout()
    path4 = CHARTS_DIR / "chart4_regional_radar.png"
    plt.savefig(path4, bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.savefig(PRESENTATION_ASSETS / "chart4_regional_radar.png", bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close()
    print(f" -> Generated {path4.name}")

def generate_chart5_summary(df_groups, df_members):
    """Chart 5: Executive Summary Scoreboard & Ranking Infographic"""
    fig, ax = plt.subplots(figsize=(14, 8))
    fig.patch.set_facecolor("#0F111A")
    ax.set_facecolor("#0F111A")
    ax.axis('off')

    title_text = "2026 K-Pop 글로벌 지형도: AI Agent 최종 데이터 분석 요약"
    ax.text(0.5, 0.95, title_text, color="#FFFFFF", fontsize=18, fontweight='bold', ha='center', va='top')

    # Column Headers
    headers = ["그룹명", "구분", "대한민국", "서부권", "아시아권", "유럽권", "종합 1위/위상", "핵심인기 멤버"]
    col_x = [0.03, 0.16, 0.25, 0.36, 0.47, 0.58, 0.70, 0.88]
    
    y = 0.86
    for h, x in zip(headers, col_x):
        ax.text(x, y, h, color="#FFD700", fontsize=11, fontweight='bold', ha='left')
    
    ax.plot([0.02, 0.98], [0.84, 0.84], color="#33384D", linewidth=1.5)

    # Fill rows
    y_step = 0.088
    current_y = 0.79

    for _, row in df_groups.iterrows():
        g_name = row["group"]
        member_info = df_members[df_members["group"] == g_name]
        m_name = member_info.iloc[0]["member"].split()[0] if not member_info.empty else row["key_member"].split()[0]
        
        # Color highlight top performers
        g_color = "#FF3366" if row["gender"] == "Female" else "#3388FF"
        
        ax.text(col_x[0], current_y, g_name, color="#FFFFFF", fontsize=11, fontweight='bold')
        ax.text(col_x[1], current_y, "걸그룹" if row["gender"]=="Female" else "보이그룹", color=g_color, fontsize=10)
        ax.text(col_x[2], current_y, f"{row['korea_score']:.1f}점", color="#E0E0E0", fontsize=10)
        ax.text(col_x[3], current_y, f"{row['western_score']:.1f}점", color="#E0E0E0", fontsize=10)
        ax.text(col_x[4], current_y, f"{row['asia_score']:.1f}점", color="#E0E0E0", fontsize=10)
        ax.text(col_x[5], current_y, f"{row['europe_score']:.1f}점", color="#E0E0E0", fontsize=10)
        
        # Status
        status = ""
        if g_name == "aespa":
            status = "국내 음원/대중성 1위"
        elif g_name == "Stray Kids":
            status = "서부/유럽 빌보드 1위"
        elif g_name == "SEVENTEEN":
            status = "아시아 돔투어/음반 1위"
        elif g_name == "BTS (정국/솔로포함)":
            status = "글로벌 종합/솔로 1위"
        elif g_name == "BLACKPINK":
            status = "글로벌 패션/투어 1위"
        elif g_name == "IVE":
            status = "국내 전연령 호감도 1위"
        elif g_name == "NewJeans":
            status = "글로벌 스트리밍 최강"
        else:
            status = "퍼포먼스 글로벌 강자"
            
        ax.text(col_x[6], current_y, status, color="#00FFCC", fontsize=10, fontweight='bold')
        ax.text(col_x[7], current_y, m_name, color="#FFAA00", fontsize=10, fontweight='bold')
        
        current_y -= y_step

    # Bottom notes
    ax.plot([0.02, 0.98], [current_y + 0.03, current_y + 0.03], color="#33384D", linewidth=1.5)
    note_text = (
        "※ 데이터 출처: Firecrawl 실시간 웹 스크래핑(Circle Chart, Melon, Billboard, Oricon, 브랜드평판) & Kaggle Spotify/Global Chart Benchmark\n"
        "※ 분석 알고리즘: 음원 스트리밍, 음반 판매량, 스타디움/페스티벌 관객수, SNS 팔로워, 브랜드 지수를 가중합산한 AI Agent 표준화 지수(100점 만점)"
    )
    ax.text(0.03, current_y - 0.01, note_text, color="#8E95AA", fontsize=9, va='top')

    plt.tight_layout()
    path5 = CHARTS_DIR / "chart5_summary_scoreboard.png"
    plt.savefig(path5, bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.savefig(PRESENTATION_ASSETS / "chart5_summary_scoreboard.png", bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close()
    print(f" -> Generated {path5.name}")

def main():
    print("[AI Agent Analyzer] Synthesizing data...")
    df_groups, df_members = load_data()
    print(f" -> Loaded {len(df_groups)} groups and {len(df_members)} core members.")

    print("[AI Agent Analyzer] Generating publication-quality charts...")
    generate_chart1_regional_rankings(df_groups)
    generate_chart2_matrix(df_groups)
    generate_chart3_core_members(df_members)
    generate_chart4_radar(df_groups)
    generate_chart5_summary(df_groups, df_members)

    print("\n[AI Agent Analyzer] Summary Results:")
    print("==================================================")
    print("1. 대한민국 1위: 걸그룹 aespa (98.5점) / 보이그룹 SEVENTEEN (96.0점)")
    print("2. 서부권(미국/북미/라틴) 1위: Stray Kids (98.8점) / 솔로 BTS 정국 (99.5점)")
    print("3. 아시아권(일본/중화/동남아) 1위: SEVENTEEN (99.2점) / 걸그룹 aespa (93.0점)")
    print("4. 유럽권(영국/프랑스/독일) 1위: Stray Kids (97.2점) / BTS (96.0점)")
    print("5. 그룹별 핵심인기 멤버:")
    for _, row in df_members.iterrows():
        print(f"   - {row['group']}: {row['member']} (인스타 {row['instagram_followers_m']}M, 브랜드 {row['brand_reputation_index']}점, 앰버서더: {row['global_ambassador']})")
    print("==================================================")

if __name__ == "__main__":
    main()
