import pandas as pd
import scipy.stats as stats
import statsmodels.api as sm
from statsmodels.formula.api import ols


def analyze_linkedin_data(file_path="activity_data.csv"):
    """
    Reads LinkedIn activity data from a CSV, adds gender and content categories,
    and performs statistical analysis to see what factors impact engagement rates.
    """
    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        print(
            "Please make sure 'activity_data.csv' is in the same directory as the script."
        )
        return

    # --- Data Cleaning and Preparation ---
    df["Person"] = df["Person"].str.strip()
    df["Like count"] = pd.to_numeric(df["Like count"], errors="coerce")
    df.dropna(subset=["Like count"], inplace=True)
    df["Like count"] = df["Like count"].astype(int)

    # Add Gender column based on the person
    gender_map = {"Cindy Gallop": "Woman", "Jane Evans": "Woman", "Matt Lawton": "Man", "Tyler Diderich": "Man"}
    df["Gender"] = df["Person"].map(gender_map)

    # Add follower counts
    follower_map = {"Cindy Gallop": 130000, "Jane Evans": 17000, "Matt Lawton": 9000}
    df["Follower Count"] = df["Person"].map(follower_map)

    # Calculate Engagement Rate (Likes per 10,000 Followers)
    df["Engagement Rate"] = (df["Like count"] / df["Follower Count"]) * 10000

    # Rename columns for easier use in formulas
    df.rename(
        columns={"Post type": "Post_type", "Post content": "Post_content"}, inplace=True
    )

    print("--- Statistical Analysis of Engagement Rate ---")
    print(
        "Using t-tests and ANOVA to test for significant differences in mean engagement."
    )
    print("A p-value < 0.05 indicates a statistically significant result.\n")

    # --- 1. Analysis by Gender ---
    print("## 1. Analysis by Gender (Man vs. Woman)")
    group_man = df["Engagement Rate"][df["Gender"] == "Man"]
    group_woman = df["Engagement Rate"][df["Gender"] == "Woman"]
    t_stat, p_val = stats.ttest_ind(group_man, group_woman, equal_var=False)
    print(f"T-statistic: {t_stat:.4f}")
    print(f"P-value: {p_val:.4f}")
    if p_val < 0.05:
        print(
            "Result: There is a statistically significant difference in engagement rates between men and women.\n"
        )
    else:
        print(
            "Result: There is no statistically significant difference in engagement rates between men and women.\n"
        )

    # --- 2. Analysis by Post Type ---
    print("## 2. Analysis by Post Type (Personal vs. Repost)")
    type_groups = [
        df["Engagement Rate"][df["Post_type"] == p_type]
        for p_type in df["Post_type"].unique()
    ]
    f_val, p_val = stats.f_oneway(*type_groups)
    print(f"F-statistic: {f_val:.4f}")
    print(f"P-value: {p_val:.4f}")
    if p_val < 0.05:
        print(
            "Result: There is a statistically significant difference between Personal posts and Reposts.\n"
        )
    else:
        print(
            "Result: There is no statistically significant difference between Personal posts and Reposts.\n"
        )

    # --- 3. Analysis by Post Content ---
    print("## 3. Analysis by Post Content (Top Categories)")
    # To run a meaningful test, we only include content categories with enough posts.
    min_samples = 5
    content_counts = df["Post_content"].value_counts()
    frequent_content = content_counts[content_counts >= min_samples].index
    df_filtered_content = df[df["Post_content"].isin(frequent_content)]

    content_groups = [
        df_filtered_content["Engagement Rate"][
            df_filtered_content["Post_content"] == content
        ]
        for content in frequent_content
    ]
    if len(content_groups) > 1:
        f_val, p_val = stats.f_oneway(*content_groups)
        print(f"Comparing top categories: {list(frequent_content)}")
        print(f"F-statistic: {f_val:.4f}")
        print(f"P-value: {p_val:.4f}")
        if p_val < 0.05:
            print(
                "Result: There is a statistically significant difference based on post content.\n"
            )
        else:
            print(
                "Result: There is no statistically significant difference based on post content.\n"
            )
    else:
        print("Not enough data for a meaningful comparison across content types.\n")

    # --- 4. Advanced Analysis: Three-Way ANOVA (Gender, Post Type, and Content) ---
    print("## 4. Advanced: Three-Way ANOVA (All Factors)")
    print(
        "This powerful test looks at all factors at once to find the most important drivers of engagement."
    )
    try:
        # Using the filtered dataframe to ensure robust results
        model = ols(
            'Q("Engagement Rate") ~ C(Gender) + C(Post_type) + C(Post_content)',
            data=df_filtered_content,
        ).fit()
        anova_table = sm.stats.anova_lm(model, typ=2)
        print(anova_table)
        print("\nInterpretation of Three-Way ANOVA:")
        print("- C(Gender): The effect of gender, controlling for other factors.")
        print("- C(Post_type): The effect of post type, controlling for other factors.")
        print(
            "- C(Post_content): The effect of content, controlling for other factors."
        )
        print("\nCheck the 'PR(>F)' column for the p-value.")
    except Exception as e:
        print(f"Could not perform Three-Way ANOVA. Error: {e}")


if __name__ == "__main__":
    analyze_linkedin_data()
