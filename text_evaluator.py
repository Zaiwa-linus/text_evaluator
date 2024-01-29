import pandas as pd
import sys
import tty
import termios
import os
import time

def getch():
    """ キーボードから1文字読み込む関数（Mac/Linux用） """
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

def evaluate_texts(csv_path):
    # CSVファイルを読み込む
    df = pd.read_csv(csv_path)

    # データを 'key' 列に基づいて並び替える
    df = df.sort_values(by='key')

    # 'evaluation'カラムをDataFrameに追加（既に存在していなければ）
    if 'evaluation' not in df.columns:
        df['evaluation'] = None

    # 評価の進捗と時間の追跡用変数
    start_times = []  # 最新10回の開始時間

    # 各テキストに対して評価を収集
    for index, row in df.iterrows():
        # 進捗情報の表示
        total = df.shape[0]
        completed = df['evaluation'].count()
        progress = (completed / total) * 100
        remaining = total - completed
        print(f"\n進捗: {progress:.2f}% 完了, 残り: {remaining}件")

        # 処理速度と残り時間の推定
        if len(start_times) == 10:
            avg_time = sum(start_times) / 10
            estimated_time = avg_time * remaining
            print(f"直近10回の平均処理時間: {avg_time:.2f}秒, 推定残り時間: {estimated_time:.2f}秒")
        elif len(start_times) > 0:
            avg_time = sum(start_times) / len(start_times)
            print(f"直近{len(start_times)}回の平均処理時間: {avg_time:.2f}秒")

        print("\n---\n")  # 区切り線を表示
        print(f"Key: {row['key']}\nPrompt: {row['prompt']}\nResult: {row['result']}\n")

        start_time = time.time()  # 評価開始時間

        # 正しい評価が入力されるまでユーザに尋ねる
        while True:
            print("このテキストを1から5で評価、または0で終了: ", end="", flush=True)
            evaluation = getch()  # キーボードからの1文字を受け取る
            print(evaluation)  # 入力された評価を表示

            if evaluation in ['1', '2', '3', '4', '5']:
                end_time = time.time()  # 評価終了時間
                elapsed_time = end_time - start_time  # 経過時間
                start_times.append(elapsed_time)
                if len(start_times) > 10:
                    start_times.pop(0)  # 最新10回のみ保持
                break
            elif evaluation == '0':
                # 現在の状態を保存して終了
                df.to_csv(csv_path, index=False)
                print("評価の途中結果を保存してプログラムを終了します。")
                return
            else:
                print("評価は1から5の数字、または0で終了してください。")

        # 評価をDataFrameに記録
        df.at[index, 'evaluation'] = evaluation

        # 10回ごとにCSVファイルに保存
        if (index + 1) % 10 == 0:
            df.to_csv(csv_path, index=False)
            print(f"{index + 1}件のテキストの評価後、ファイルを保存しました。")

    # 最後の評価が保存される
    df.to_csv(csv_path, index=False)
    print("全ての評価がCSVファイルに保存されました。")

def main():
    while True:
        # ユーザにCSVファイルのパスを尋ねる
        csv_path = input("評価するテキストが含まれているCSVファイルのパスを入力してください: ")
        # 相対パスを絶対パスに変換
        csv_path = os.path.abspath(csv_path)

        # ファイルの存在とフォーマットを確認
        if os.path.exists(csv_path):
            try:
                # CSVファイルを読み込んで確認
                pd.read_csv(csv_path)
                break
            except pd.errors.ParserError:
                print("指定されたファイルはCSVフォーマットではありません。")
        else:
            print("指定されたファイルが存在しません。")

    # 評価処理の実行
    evaluate_texts(csv_path)

if __name__ == "__main__":
    main()
