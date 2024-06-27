import sys
import pandas as pd
import matplotlib.pyplot as plt


def main():
    usage1 = ["mix", "query_only", "updates_only"]
    usage2 = ["semi", "full"]
    usage3 = ["d-trees", "stt-c", "stt-rs", "all"]
        
    if len(sys.argv) != 4 or sys.argv[1] not in usage1 or sys.argv[2] not in usage2 or sys.argv[3] not in usage3:
        exit(f"Usage: {sys.argv[0]} <{'|'.join(usage1)}> <{'|'.join(usage2)}> <{'|'.join(usage3)}>")
    
    impls = []
    if sys.argv[3] == "all":
        usage3.remove("all")
        impls = usage3
    else:
        impls = [sys.argv[3]]

    pd.set_option('colheader_justify', 'center')
    
    splay_top_tree_df = pd.read_json(f"results/connectivity/{sys.argv[1]}/splay-top-tree.jsonl", lines=True, orient="records")
    splay_top_tree_df = splay_top_tree_df.rename(columns={"median": "time_ns", "num_edges": "num_queries"})
    splay_top_tree_df = pd.concat([splay_top_tree_df['name'], splay_top_tree_df['num_vertices'], splay_top_tree_df['num_queries'], splay_top_tree_df['time_ns'], ], axis=1)
    splay_top_tree_df = splay_top_tree_df[(splay_top_tree_df['name'] == f"Splay top tree {sys.argv[2]} splay")]
    splay_top_tree_df = splay_top_tree_df.reset_index(drop=True)
    
    df = None
    for impl in impls:
        
        impl_df = pd.read_json(f"results/connectivity/{sys.argv[1]}/{impl}.jsonl", lines=True, orient="records")
        impl_df = impl_df.rename(columns={"median": "time_ns", "num_edges": "num_queries"})
        impl_df = pd.concat([impl_df['name'], impl_df['num_vertices'], impl_df['num_queries'], impl_df['time_ns'], ], axis=1)
        impl_df = impl_df.reset_index(drop=True)

        for ds in impl_df["name"].unique():
            filt_df = impl_df[(impl_df['name'] == ds)].reset_index(drop=True)
            print(filt_df)
            filt_df['ratio'] = splay_top_tree_df[['time_ns']].div(filt_df['time_ns'], axis= 0)
            print(filt_df)
            
            if df is not None:
                df = pd.concat( [df, filt_df]).reset_index(drop=True)
            else:
                df = filt_df
        
    print(df)

    df = df.pivot(index='num_vertices', columns='name', values='ratio').div(1000*1000).reset_index()
    df = df.set_index('num_vertices')
    df.plot.line(loglog=False, xlabel="Vertices", ylabel="Ratio")
    plt.show()

if __name__ == "__main__":
    main()