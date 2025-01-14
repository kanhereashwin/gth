#!/usr/bin/env python3
#######################################################################
# Author(s):    D. Knowles
# Date:         08 Dec 2020
# Desc:         Plotting functions
#######################################################################

import os
import datetime
import configparser
import pandas as pd
from math import ceil
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from pandas.plotting import register_matplotlib_converters

# something weird to avoid a pandas/matplotlib conversion warning
register_matplotlib_converters()

# read configuration file
config = configparser.ConfigParser()
file_dir = os.path.dirname(os.path.realpath(__file__))
# add some default file paths for later
log_dir = file_dir + "/../log/"
repos_dir = log_dir + "repos/"
an_dir = log_dir + "analytics/"

def create_plots(verbose=False):
    """
    Desc:
        create a bunch of plots as desired
    Input(s):
        verbose (bool) : print verbose debugging statements
    Output(s):
        None
    """
    # the number of repos that should be included. None means that all
    # repositories will be included in the graph data (except for those
    # with null data)
    top_num = None

    if verbose:
        print("beginning to create plots...")

    # plot cumulative figures
    fig1 = plot_daily_metrics("clones_daily","cumsum",top_num)
    fig2 = plot_daily_metrics("clones_uniques_daily","cumsum",top_num)
    fig3 = plot_daily_metrics("views_daily","cumsum",top_num)
    fig4 = plot_daily_metrics("views_uniques_daily","cumsum",top_num)

    # plot daily figures
    fig5 = plot_daily_metrics("clones_daily","daily",top_num)
    fig6 = plot_daily_metrics("clones_uniques_daily","daily",top_num)
    fig7 = plot_daily_metrics("views_daily","daily",top_num)
    fig8 = plot_daily_metrics("views_uniques_daily","daily",top_num)

    update_repo_plots(verbose)

    plt.close("all")

    if verbose:
        print("...finished creating plots")

def create_email_plots(date_cur, date_prev = None):
    """
    Desc:
        create and save some plots for use in an email
    Input(s):
        date_cur (string: YYYY-MM-DD) : date of current analytics file
        date_prev (string: YYYY-MM-DD) : date of previous analytics file
    Output(s):
        fig_paths (list : [string,string,...]) : list of strings of the
            location of where each figure is saved
    """
    # the number of repos that should be included. None means that all
    # repositories will be included in the graph data (except for those
    # with null data)
    top_num = 10
    # all data after this date (inclusive) will be plotted
    date_filter = date_prev
    # paths to each figure
    fig_paths = []

    fig1 = plot_daily_metrics("clones_daily","cumsum",
                              top_num,date_filter)
    plt.title("Cumulative Daily Clones")
    fig1_path = an_dir+date_cur+"/cumulative_" + "clones_daily.png"
    fig_paths.append(fig1_path)
    save_and_close(fig1,fig1_path)

    fig2 = plot_daily_metrics("views_daily","cumsum",
                              top_num,date_filter)
    plt.title("Cumulative Daily Views")
    fig2_path = an_dir+date_cur+"/cumulative_" + "views_daily.png"
    fig_paths.append(fig2_path)
    save_and_close(fig2,fig2_path)

    fig3 = plot_daily_metrics("clones_uniques_daily","daily",
                              top_num,date_filter)
    plt.title("Daily Unique Clones")
    fig3_path = an_dir+date_cur+"/daily_" + "clones_uniques_daily.png"
    fig_paths.append(fig3_path)
    save_and_close(fig3,fig3_path)

    fig4 = plot_daily_metrics("views_uniques_daily","daily",
                              top_num,date_filter)
    plt.title("Daily Unique Views")
    fig4_path = an_dir+date_cur+"/daily_" + "views_uniques_daily.png"
    fig_paths.append(fig4_path)
    save_and_close(fig4,fig4_path)

    fig5 = plot_daily_metrics("views_daily","cumsum",top_num)
    plt.title("Cumulative History of Daily Views")
    fig5_path = an_dir+"/cumulative_views_daily.png"
    fig_paths.append(fig5_path)
    save_and_close(fig5,fig5_path)

    return fig_paths

def update_repo_plots(verbose=False):
    """
    Desc:
        update all repo plots. This function in particular takes a long
        amount of time. You can not call this function if for some
        reason you need to run this code faster
    Input(s):
        verbose (bool) : print verbose debugging statements
    Output(s):
        None
    """
    # get all repository directories
    repos_dirs = [content for content in os.listdir(repos_dir)
               if os.path.isdir(os.path.join(repos_dir,content))]

    for dd,repo_dir in enumerate(repos_dirs):
        if verbose:
            print("creating repo plots for ",dd,"/",len(repos_dirs),": ",repo_dir)
        # plot cumulative figures
        plot_repo_metric(repo_dir,"clones_daily","cumsum")
        plot_repo_metric(repo_dir,"clones_uniques_daily","cumsum")
        plot_repo_metric(repo_dir,"views_daily","cumsum")
        plot_repo_metric(repo_dir,"views_uniques_daily","cumsum")

        # plot daily figures
        plot_repo_metric(repo_dir,"clones_daily","daily")
        plot_repo_metric(repo_dir,"clones_uniques_daily","daily")
        plot_repo_metric(repo_dir,"views_daily","daily")
        plot_repo_metric(repo_dir,"views_uniques_daily","daily")

        # plot other figures
        plot_repo_metric(repo_dir,"forks","daily")
        plot_repo_metric(repo_dir,"stars","daily")

def plot_repo_metric(repo_dir,metric_name,type):
    """
    Desc:
        plots individual repository metrics and saves the plots
    Input(s):
        repo_dir (string) : filepath to the repository logs
        metric_name (string) : name for metric and column name
        type (string) : either "cumsum" or "daily". "cumsum" will plot
            the cumulative sum of the column over time while "daily"
            will plot the daily change over time
    Output(s):
        None
    """

    # read in the metric data
    metric_df = pd.read_csv(repos_dir+repo_dir+"/"+metric_name+".csv")

    # don't try to plot something if there's only one value
    if len(metric_df.index) < 2:
        return

    # set up figure and size it
    fig,ax = plt.subplots()
    fig.set_size_inches(8, 4.5)

    # convert dates to datetime
    metric_dates = metric_df["date"].values
    metric_dates = [datetime.datetime.strptime(d,"%Y-%m-%d").date()
                  for d in metric_dates]

    if type == "cumsum":
        # create a column with the cumulative summation
        metric_df["cumsum"] = metric_df[metric_name].cumsum()
        plt.plot(metric_dates,metric_df["cumsum"])
    elif type == "daily":
        plt.plot(metric_dates,metric_df[metric_name])

    # create locations on axis
    locator = mdates.AutoDateLocator()
    ax.xaxis.set_major_locator(locator)

    # format dates
    formatter = mdates.DateFormatter("%Y-%m-%d")
    ax.xaxis.set_major_formatter(formatter)

    # rotate and size the date labels
    ax.xaxis.set_tick_params(rotation=60, labelsize=10)

    if type == "cumsum":
        plt.title("cumulative " + metric_name + " over Time")
        plt_file = repos_dir+repo_dir + "/cumulative_ " + \
                   metric_name + ".png"
    elif type == "daily":
        plt.title(metric_name + " over Time")
        plt_file = repos_dir+repo_dir+"/daily_ " + metric_name + ".png"

    # give everything enough room
    fig.tight_layout()

    # save the plot
    plt.savefig(plt_file,
            format="png",
            bbox_inches="tight")

    plt.close(fig)

def plot_daily_metrics(col_name, type = "daily",
                       top_num = None, date_filter = None):
    """
    Desc:
        plot and daily metrics. The plots get saved to default location
        if there is no date filter implmented
    Input(s):
        col_name (string) : name for filename and column name
        type (string) : either "cumsum" or "daily". "cumsum" will plot
            the cumulative sum of the column over time while "daily"
            will plot the daily change over time
        top_num (int) : number of top repositories (according to
            cumulative sum) to show in the graph. Repos with a
            cumulative value of 0 will still not be plotted
        date_filter (string : "YYYY-MM-DD") : all data after this date
            (inclusive) will be plotted. None means all data will be
            plotted
    Output(s):
        fig (matplotlib figure) : new figure
    """

    # set up figure and size it
    fig,ax = plt.subplots()
    fig.set_size_inches(8, 4.5)

    # get all repository directories
    repos_dirs = [content for content in os.listdir(repos_dir)
               if os.path.isdir(os.path.join(repos_dir,content))]

    # if we are plotting all the repositories
    if top_num == None or top_num > len(repos_dirs):
        for repo_dir in repos_dirs:
            # read in the corresponding csv file
            repo_df = pd.read_csv(repos_dir+repo_dir+"/"+col_name+".csv")

            # filter by date
            if date_filter != None:
                filter_index = repo_df.index[repo_df["date"] == date_filter].tolist()
                if len(filter_index) == 0:
                    print("no matching data for date filter")
                else:
                    truncate_index = filter_index[0]
                    repo_df = repo_df.truncate(before=truncate_index)

            # create a column with the cumulative summation
            repo_df["cumsum"] = repo_df[col_name].cumsum()

            # convert dates to datetime
            repo_dates = repo_df["date"].values
            repo_dates = [datetime.datetime.strptime(d,"%Y-%m-%d").date()
                          for d in repo_dates]

            # ignore data with all zeros
            if repo_df["cumsum"].values[-1] > 1:
                if type == "cumsum":
                    plt.plot(repo_dates,repo_df["cumsum"],
                                 label=repo_dir)
                elif type == "daily":
                    plt.plot(repo_dates,repo_df[col_name],
                                 label=repo_dir)

    # else if we're only plotting the top number (top_num) of repos
    else:
        top_sums = []
        for repo_dir in repos_dirs:
            # read in the corresponding csv file
            repo_df = pd.read_csv(repos_dir+repo_dir+"/"+col_name+".csv")

            # filter by date
            if date_filter != None:
                filter_index = repo_df.index[repo_df["date"] == date_filter].tolist()
                if len(filter_index) == 0:
                    print("no matching data for date filter")
                else:
                    truncate_index = filter_index[0]
                    repo_df = repo_df.truncate(before=truncate_index)

            # create a column with the cumulative summation
            repo_df["cumsum"] = repo_df[col_name].cumsum()

            top_sums.append((repo_df["cumsum"].values[-1],repo_dir))

        # sort and go from highest to lowest
        top_sums.sort()
        top_sums.reverse()
        top_sums = top_sums[:top_num]

        for top in top_sums:
            # read in the corresponding csv file
            repo_df = pd.read_csv(repos_dir+top[1]+"/"+col_name+".csv")

            # filter by date
            if date_filter != None:
                filter_index = repo_df.index[repo_df["date"] == date_filter].tolist()
                if len(filter_index) == 0:
                    print("no matching data for date filter")
                else:
                    truncate_index = filter_index[0]
                    repo_df = repo_df.truncate(before=truncate_index)

            # create a column with the cumulative summation
            repo_df["cumsum"] = repo_df[col_name].cumsum()

            # convert dates to datetime
            repo_dates = repo_df["date"].values
            repo_dates = [datetime.datetime.strptime(d,"%Y-%m-%d").date()
                          for d in repo_dates]

            # ignore data with all zeros
            if repo_df["cumsum"].values[-1] > 1:
                if type == "cumsum":
                    plt.plot(repo_dates,repo_df["cumsum"],
                                 label=top[1])
                elif type == "daily":
                    plt.plot(repo_dates,repo_df[col_name],
                                 label=top[1])

    # create locations on axis
    locator = mdates.AutoDateLocator()
    ax.xaxis.set_major_locator(locator)

    # format dates
    formatter = mdates.DateFormatter("%Y-%m-%d")
    ax.xaxis.set_major_formatter(formatter)

    # rotate and size the date labels
    ax.xaxis.set_tick_params(rotation=60, labelsize=10)

    # add legend
    lg = plt.legend(bbox_to_anchor=(1.0, 1.0), loc="upper left")

    if type == "cumsum":
        plt.title("cumulative " + col_name + " over time")
        plt_file = an_dir + "cumulative_" + col_name + ".png"
    elif type == "daily":
        plt.title(col_name + " over time")
        plt_file = an_dir + "daily_" + col_name + ".png"

    # give everything enough room
    fig.tight_layout()

    # save the figure if no date filter
    if date_filter == None:
        plt.savefig(plt_file,
                format="png",
                bbox_extra_artists=(lg,),
                bbox_inches="tight")

    return fig

def save_and_close(fig,plt_file):
    """
    Desc:
        saves and closes the figure
    Input(s):
        fig (matplotlib fig) : figure object
        plt_file (string) : filepath for the figure
    Output(s):
        None
    """

    fig.savefig(plt_file,
            format="png",
            bbox_inches="tight")
    plt.close(fig)
