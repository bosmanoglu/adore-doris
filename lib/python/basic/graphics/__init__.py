import numpy as np
import pylab as P
import basic
import scipy
from arcs import arcs 
def matshowClick(A, value=True, vmin=None, vmax=None):
    def onclick(event):
        try:
            y=np.round(event.xdata);
        except:
            return
        x=np.round(event.ydata);
        if value==True:          
            print (x,y, A[x,y])
        else:
            print (x,y)
        
    s=basic.nonaninf(A).std();
    m=basic.nonaninf(A).mean();
    if vmin is None:
        vmin=m-2*s
    if vmax is None:
        vmax=m+2*s
            
    fig=P.figure();
    ax=fig.add_subplot(111);ax.matshow(A, vmin=vmin, vmax=vmax);
    fig.canvas.mpl_connect('button_press_event', onclick);
    return fig        

def imshowsc(A,n=2):
    """
    figureHandle=matshow(array2d);
    Automatically sets colorbar to 1 sigma of the data in window.
    """
    print "DOES NOT WORK"
    def onclick(event):
        limits=P.axis();
        B=A[limits[2]:limits[3],limits[0]:limits[1]]
        #P.imshow(B);
        s=B[~np.isnan(B)].std();
        ax.clim([-2*s,2*s]);
        
    fig=P.figure();
    ax=fig.add_subplot(111);ax.matshow(A);
    fig.canvas.mpl_connect('button_press_event', onclick);
    return fig

def clickScat(array2d, array3d, xScat=None, xerror3d=None, yerror3d=None, array3d2=None, xerror3d2=None, yerror3d2=None, fn=None, xMap=None, yMap=None, 
    modelError=False, ylimScat=None):
    """
    figureHandles=clickScat(array2d, array3d, xScat=None, xerror3d=None, yerror3d=None, array3d2=None, xerror3d2=None, yerror3d2=None, fn=None, xMap=None, yMap=None):
    xScat: x-axis variables for Scatter Plot. Has to be the same length as last dimension of array3d.shape[2]
    xerror3d: errorbars for x-axis. two sided. 
    fn:'annual'
    """
    import insar
    dateaxis=False;
    if xScat is None:
        xScat=np.r_[0:array3d.shape[2]];
    elif isinstance(xScat[0], P.matplotlib.dates.datetime.date):
        xScat=P.matplotlib.dates.date2num(xScat);
        dateaxis=True;

    def onclick(event):
        P.figure(fh.number);
        P.clf();
        #ax = P.gca()
        #inv = ax.transData.inverted()
        #A=inv.transform((event.x,  event.y))
        #A[1]=np.int(np.round((1-A[1])*array2d.shape[1])) 
        #A[0]=np.int(np.round((A[0])*array2d.shape[0]))
        try:
            y=np.round(event.xdata);
        except:
            return
        x=np.round(event.ydata);        
        #ARRAY MAPPING IS first axis y(rows) and second axis is cols (x)
        if all(np.isnan(array3d[x, y,:])):
            #if there are no points to plot (all nan) then return
            return
        
        #Plot second scatter data.
        if array3d2 is not None:        
            if isinstance(array3d2, list):
                if yerror3d is None:
                    w=np.ones(array3d[x, y,:].shape);
                else:
                    w=basic.rescale(1./yerror3d[x,y,:], [1,2])
                markers=['*','+','s','d','x','v','<','>','^']
                m=0;
                for arr in array3d2:  
                    print ("%d, %d, %d" % (x,y,m))                  
                    P.scatter(xScat, arr[x, y,:], marker=markers[m]);
                    idx=~( np.isnan(arr[x, y,:]) | np.isnan(array3d[x, y,:]))
                    #c=insar.crosscorrelate(basic.nonan(w[idx]*arr[x, y,idx]),basic.nonan(w[idx]*array3d[x, y,idx]))
                    slope, intercept, r_value, p_value, std_err = scipy.stats.linregress(basic.nonan(w[idx]*arr[x, y,idx]), basic.nonan(w[idx]*array3d[x, y,idx]))
                    P.annotate(str("r2[%s]: %0.2f" % (markers[m],r_value)), (0,0.9-m*0.05), xycoords='axes fraction')                    
                    m=m+1;
            else:            
                if xerror3d2 is None:
                    xerr=None;
                else:
                    xerr=xerror3d2[x,y,:]
                if yerror3d2 is None:
                    yerr=None;
                else:
                    yerr=yerror3d2[x, y,:]
                P.errorbar(xScat,array3d2[x, y,:], xerr=xerr, yerr=yerr, marker='*', fmt='o');

        #Plot function result as scatter data.
        p=None            
        if fn is not None:
            if fn=='linear_amplitude_annual':
                dataMask=~np.isnan(array3d[x, y,:])
                p0=np.array([1,0,0,basic.nonan(array3d[x, y,:]).mean() ])
                fitfun=lambda p: (p[0]+p[1]*xScat[dataMask]/365. )* np.cos(2*np.pi*xScat[dataMask]/365.+p[2]) + p[3]
                xScat2=np.linspace(xScat.min(),xScat.max())
                fitfun2=lambda p: (p[0]+p[1]*xScat2/365.) * np.cos(2*np.pi*xScat2/365.+p[2]) + p[3]
                #errfun=lambda p: sum(abs(basic.nonan(array3d[x, y,:])-fitfun(p)));
                if yerror3d is None:
                    w=np.ones(array3d[x, y,:].shape);
                else:
                    w=basic.rescale(1./yerror3d[x,y,:], [1,2])
                errfun=lambda p: basic.nonan(w*array3d[x, y,:])-w[dataMask]*fitfun(p);
                #p=scipy.optimize.fmin_powell(errfun, p0)
                p=scipy.optimize.leastsq(errfun, p0);
                p=p[0];
                P.scatter(xScat[dataMask], fitfun(p), marker='^');                
                sortedxy=  np.squeeze(np.dstack([xScat2, fitfun2(p)]));
                sortedxy=sortedxy[sortedxy[:,0].argsort(),:]
                P.plot(sortedxy[:,0], sortedxy[:,1]);
                slope, intercept, r_value, p_value, std_err = scipy.stats.linregress(basic.nonan(w*array3d[x, y,:]),w[dataMask]*fitfun(p))
                P.annotate(str("a0:%0.2f\na1:%0.2f\npha:%0.2f\nbias:%0.2f\nr2:%0.2f" % (p[0], p[1], p[2], p[3], r_value**2.)), (0.8,0.8), xycoords='axes fraction')
            elif fn=='quadratic_amplitude_annual':
                dataMask=~np.isnan(array3d[x, y,:])
                p0=np.array([1,0,0,0,basic.nonan(array3d[x, y,:]).mean() ])
                fitfun=lambda p: (p[0]+p[1]*xScat[dataMask]/365.+p[2]*(xScat[dataMask]/365.)**2. )* np.cos(2*np.pi*xScat[dataMask]/365.+p[3]) + p[4]
                xScat2=np.linspace(xScat.min(),xScat.max())
                fitfun2=lambda p: (p[0]+p[1]*xScat2/365.+p[2]*(xScat2/365.)**2.) * np.cos(2*np.pi*xScat2/365.+p[3]) + p[4]
                #errfun=lambda p: sum(abs(basic.nonan(array3d[x, y,:])-fitfun(p)));
                if yerror3d is None:
                    w=np.ones(array3d[x, y,:].shape);
                else:
                    w=basic.rescale(1./yerror3d[x,y,:], [1,2])
                errfun=lambda p: basic.nonan(w*array3d[x, y,:])-w[dataMask]*fitfun(p);
                #p=scipy.optimize.fmin_powell(errfun, p0)
                p=scipy.optimize.leastsq(errfun, p0);
                p=p[0];
                P.scatter(xScat[dataMask], fitfun(p), marker='^');                
                sortedxy=  np.squeeze(np.dstack([xScat2, fitfun2(p)]));
                sortedxy=sortedxy[sortedxy[:,0].argsort(),:]
                P.plot(sortedxy[:,0], sortedxy[:,1]);
                slope, intercept, r_value, p_value, std_err = scipy.stats.linregress(basic.nonan(w*array3d[x, y,:]),w[dataMask]*fitfun(p))
                P.annotate(str("a0:%0.2f\na1:%0.2f\na2:%0.2f\npha:%0.2f\nbias:%0.2f\nr2:%0.2f" % (p[0], p[1], p[2], p[3], p[4], r_value**2.)), (0.8,0.8), xycoords='axes fraction')


            elif fn=='annual':
                dataMask=~np.isnan(array3d[x, y,:])
                p0=np.array([1,1,basic.nonan(array3d[x, y,:]).mean() ])
                fitfun=lambda p: p[0]* np.cos(2*np.pi*xScat[dataMask]/365.+p[1]) + p[2]
                xScat2=np.linspace(xScat.min(),xScat.max())
                fitfun2=lambda p: p[0]* np.cos(2*np.pi*xScat2/365.+p[1]) + p[2]
                #errfun=lambda p: sum(abs(basic.nonan(array3d[x, y,:])-fitfun(p)));
                if yerror3d is None:
                    w=np.ones(array3d[x, y,:].shape);
                else:
                    w=basic.rescale(1./yerror3d[x,y,:], [1,2])
                errfun=lambda p: basic.nonan(w*array3d[x, y,:])-w[dataMask]*fitfun(p);
                #p=scipy.optimize.fmin_powell(errfun, p0)
                p=scipy.optimize.leastsq(errfun, p0);
                p=p[0];
                P.scatter(xScat[dataMask], fitfun(p), marker='^');                
                sortedxy=  np.squeeze(np.dstack([xScat2, fitfun2(p)]));
                sortedxy=sortedxy[sortedxy[:,0].argsort(),:]
                P.plot(sortedxy[:,0], sortedxy[:,1]);
                slope, intercept, r_value, p_value, std_err = scipy.stats.linregress(basic.nonan(w*array3d[x, y,:]),w[dataMask]*fitfun(p))
                P.annotate(str("amp:%0.2f\npha:%0.2f\nbias:%0.2f\nr2:%0.2f" % (p[0], p[1], p[2], r_value**2.)), (0.8,0.8), xycoords='axes fraction')
            else:      
                p=None             
                P.scatter(xScat, fn(xScat), marker='^');       
        #convert axis to date...             
        if dateaxis:
            try:
                P.figure(fh.number).axes[0].xaxis_date(tz=None)
                P.figure(fh.number).autofmt_xdate()
            except:
                pass
        #change x y to xMap, yMap
        if yMap is not None:
            xM=ya*x+yb;
        else:
            xM=x;
        if xMap is not None:
            yM=xa*(y)+xb;
        else:
            yM=y;
        #x and y are flipped in the try/except block above. So Flip again.
        #if p is not None:
        #    P.title("x,y,[]: " + str(yM) + ", " + str(xM) + ', ' + str(p) )
        #else:
        P.title("x,y,z,z.std: " + str(yM) + ", " + str(xM) + ', ' + str(array2d[x,y]) +', ' + str(np.std(basic.nonan(array3d[x, y,:]))) )
        
        # rotate and align the tick labels so they look better
        #P.figure(fh.number).autofmt_xdate()
        # use a more precise date string for the x axis locations in the
        # toolbar
        #P.gca().fmt_xdata = mdates.DateFormatter('%Y-%m-%d')

        if xerror3d is None:
            xerr=None;
        else:
            xerr=xerror3d[x,y,:]
        if yerror3d is None:
            yerr=None;
        else:
            yerr=yerror3d[x, y,:]        
        if modelError:
            yerr=yerror3d[x, y,:] 
            yerr[dataMask]=errfun(p)
            
        P.errorbar(xScat,array3d[x, y,:], xerr=xerr, yerr=yerr, fmt='ro');
        if ylimScat is not None:
            P.ylim(ylimScat);
        ##################################
        ## END OF PLOTTING
        ##################################
        
    s=array2d[~np.isnan(array2d)].std();
    m=array2d[~np.isnan(array2d)].mean();
    fig=P.figure();ax=fig.add_subplot(111);ax.matshow(array2d, vmin=m-s, vmax=m+s);
    #fig=P.figure();ax=fig.add_subplot(111);ax.matshow(basic.wrapToInt(array2d, s), vmin=-s, vmax=s);
    if xMap is not None:
        ticks=ax.get_xticks();
        (xa,xb)=np.polyfit(np.r_[0:len(xMap)],xMap,1)
        ax.set_xticklabels(np.around(xa*ticks+xb,4));
    if yMap is not None:
        ticks=ax.get_yticks();
        (ya,yb)=np.polyfit(np.r_[len(yMap):0:-1],yMap,1)
        ax.set_yticklabels(np.around(ya*ticks+yb,4));
    
    #P.colorbar();
    cax,kw=P.matplotlib.colorbar.make_axes(ax,orientation='vertical')
    P.matplotlib.colorbar.ColorbarBase(cax, cmap=P.jet(),
                                       norm=P.normalize(vmin=m-s,vmax=m+s),
                                       orientation='vertical')
    fh=P.figure(); #should be accessible in child function?
    fig.canvas.mpl_connect('button_press_event', onclick);
    return (fig,fh)
    
def linkedImShow(im1, im2, **kwargs):
    """(ax1,ax2)=linkedImShow(im1, im2, **imshow_kwargs)
    """
    P.figure();
    ax1 = P.subplot(111)
    P.figure();
    ax2 = P.subplot(111, sharex=ax1, sharey=ax1)
    
    #ax1.set_adjustable("box-forced")
    #ax2.set_adjustable("box-forced")
    
    #arr1 = np.arange(100).reshape((10, 10))
    ax1.imshow(im1, **kwargs)
    
    #arr2 = np.arange(100, 0, -1).reshape((10, 10))
    ax2.imshow(im2, **kwargs)
    return (ax1, ax2)
    
def linkaxes(ax1, ax2):        
    ax2.set(sharex=ax1, sharey=ax1)
    
def linkfigures(fg1, fg2):
    ax1=fg1.get_axes()[0]
    ax2=fg2.get_axes()[0]
    ax2.set(sharex=ax1, sharey=ax1)

def frankotchellappa(dzdx,dzdy):
    '''frankotchellappa(dzdx,dzdy):
    '''
    dS=dzdx.shape;
    cols=dS[1];
    rows=dS[0]; 
    [wx, wy] = np.meshgrid((np.r_[1:cols+1]-(np.fix(cols/2)+1))/(cols-np.mod(cols,2)),(np.r_[1:rows+1]-(np.fix(rows/2)+1))/(rows-np.mod(rows,2)));
    wx = np.fft.ifftshift(wx); wy = np.fft.ifftshift(wy);
    DZDX = np.fft.fft2(dzdx);
    DZDY = np.fft.fft2(dzdy);
    eps=np.finfo(np.double).eps;
    Z = (-1j*wx*DZDX -1j*wy*DZDY)/(wx**2 + wy**2 + eps)
    z = np.fft.ifft2(Z).real;
    return z
    
def matscale(array, m=None, s=None, **kwargs):
    ''' matscale(array, m=None, s=None, **kwargs)
    Ex: matscale(kum.topoA[:,:,0])
    '''
    if not m:
        m=array.mean()
    if not s:
        s=array.std()
    return P.matshow(array, vmin=m-s, vmax=m+s, **kwargs);  

def matshowN(array, axis=None, titles=None, matshow_kw=dict(), subplot_kw=dict(frame_on=False), **kwargs):
    ''' matshowN(array, axis=None, titles=None, subplot_kw=dict(frame_on=False), **kwargs)
        Ex: f=matshowN(angle(kum.iG.cint[:]))
            f.tight_layout()
            basic.graphics.matshowN((residual/stdpha)**2., matshow_kw={'vmin':0, 'vmax':1})
            
        axis: If not specified, uses the axis with minimum elements.
            axis=argmin(array.shape)
    '''          
    if axis is None:
      axis=np.argmin(array.shape);
    num=array.shape[axis];
    lw=int(np.ceil(np.sqrt(num)));
    f,axarr=P.subplots(lw,lw,sharex='col',sharey='row', subplot_kw=subplot_kw, **kwargs)
    array=np.rollaxis(array, axis, 0);
    k=0;
    for ax in axarr.ravel():
      if k >= num:
        ax.set_axis_off();    
        continue
      ax.matshow(array[k,:,:], **matshow_kw);
      if titles is None:
        ax.set_title(str('%d'%k));ax.set_axis_off();
      else:
        ax.set_title(titles[k]);ax.set_axis_off();
      k=k+1;
    return f;
    
def frankotchellappaiter(dzdx,dzdy,weight=None, threshold=0.1, maxiter=10):
    '''frankotchellappaiter(dzdx,dzdy):
    '''   
    dS=dzdx.shape;
    if weight is None:
       weight=np.ones(dS);

    cols=dS[1];
    rows=dS[0]; 
    [wx, wy] = np.meshgrid((np.r_[1:cols+1]-(np.fix(cols/2)+1))/(cols-np.mod(cols,2)),(np.r_[1:rows+1]-(np.fix(rows/2)+1))/(rows-np.mod(rows,2)));
    wx = np.fft.ifftshift(wx); wy = np.fft.ifftshift(wy);
    dx=dzdx.copy()
    dy=dzdy.copy()
    
    nfilt=9.0
    corrFilter=np.array([[1,1,1],[1,1,1],[1,1,1]])/nfilt #http://docs.scipy.org/doc/scipy-0.7.x/reference/tutorial/ndimage.html
    for k in xrange(maxiter):
       dx=scipy.ndimage.filters.correlate(dx,corrFilter,mode='nearest')
       dy=scipy.ndimage.filters.correlate(dy,corrFilter,mode='nearest')

       z=frankotchellappa(dx,dy)
       gx,gy=np.gradient(z);

       rx=(weight*(gx/dzdx)).mean()
       ry=(weight*(gy/dzdy)).mean()
       dx=dzdx/rx
       dy=dzdy/ry
       
       z=frankotchellappa(dx,dy)
       gx,gy=np.gradient(z);

       c = weight*np.sqrt((dzdx-gx)**2+(dzdy-gy)**2)
       if c.mean()<threshold:
          print "cost: ", c.mean()
          break
       else:
          print "cost: ", c.mean()

       dx=dx+scipy.ndimage.filters.correlate(dzdx-gx,corrFilter, mode='nearest')
       dy=dy+scipy.ndimage.filters.correlate(dzdy-gy,corrFilter, mode='nearest')

    return z
    

def frankotchellappaiter2(dzdx,dzdy):
    '''frankotchellappaiter2(dzdx,dzdy):
    Ex:
    dzdx,dzdy=insar.cpxgradient(pf)
    uw=basic.plot.frankotchellappaiter2(dzdy,dzdx);
    matshow(angle(pf*exp(-1j*uwxy)));
    '''
    import kabum
    z=kabum.frankotchellappa(dzdx,dzdy);
    gy,gx=np.gradient(z);
    rx=basic.nonaninf(gx/dzdx).mean()
    ry=basic.nonaninf(gy/dzdy).mean()
    z=kabum.frankotchellappa(dzdx/rx,dzdy/ry);
    gy,gx=np.gradient(z);
    
    return z
    
def histogram_matching(inputArr, histogramArr=None, bins=100, zpdf=None, zbins=None):
    """histogram_matching(inputArr, histogramArr=None, bins=100, zpdf=None, zbins=None)
    """
    if (histogramArr is None) and (zpdf is None):
        print('Error: histogramArr or zpdf has to be specified')
        return 
    if (bins<=1) and (zbins is None):
        print('Skipping histogram matching: bins<=1')
        return inputArr
    if len(zbins)<=1:
        print('Skipping histogram matching: len(zbins)<=1')
        return inputArr
        
    dS=inputArr.shape
    lenS=inputArr.size
    s=basic.nonan(inputArr.ravel())

    #Limit matching to majority of the pixels.. We don't want a long trail.
    sm=s.mean()
    ss=s.std()
    sbins=P.np.linspace(sm-3*ss,sm+3*ss,bins+1);    

    spdf, sbins=P.np.histogram(s, sbins)
    spdf=spdf/P.np.double(sum(spdf))
    sk= P.np.cumsum(spdf) #spdf * P.np.triu(P.np.ones(dS)) #CDF

    #Histogram to be matched
    if zpdf is None:
        dZ=histogramArr.shape
        lenZ=histogramArr.size
        z=basic.nonan(histogramArr.ravel())
        zm=z.mean()
        zs=z.std()
        zbins=P.np.linspace(zm-3*zs,zm+3*zs,bins+1);            
        zpdf, zbins=P.np.histogram(z, zbins)
    else:
      #make zpdf match the length of bins
      zpdf=np.interp(sbins, np.linspace(zbins[0], zbins[-1], zpdf.shape[0]), zpdf);
      zbins=sbins #zbins no longer needed?.
    zpdf=zpdf/P.np.double(sum(zpdf))
    zk= P.np.cumsum(zpdf) #G(z), CDF
    
    #create the image
    p_prev=0
    z0=P.np.empty(dS)
    z0[:]=P.np.nan
    for q in xrange(0,bins):
        for p in xrange(p_prev,bins):
            if zk[p] >= sk[q]:
                #print ['replacing from ', sbins[q], ' to ', sbins[q+1] , ' with ', zbins[p]]
                p_prev=p+1
                q_last=q
                #z0[ P.np.ma.mask_or(inputArr>sbins[q], inputArr<sbins[q+1]) ] = zbins[p];
                if q==0:
                    z0[ inputArr<sbins[q+1] ] = zbins[p];
                else:
                    z0[ ((inputArr>=sbins[q]).astype(P.np.int) * (inputArr<sbins[q+1]).astype(P.np.int)).astype(P.np.bool) ] = zbins[p];
                #print ['replacing ', ((inputArr>sbins[q]).astype(P.np.int) * (inputArr<sbins[q+1]).astype(P.np.int)).sum(), ' pixels'];
                break #inner for
    #print('q %f p %f zk %f sk %f' %(q,p,zk[p], sk[q]))
    z0[inputArr>=sbins[q_last]]=zbins[p]
    
    return z0

def histogramMap(arrIn, **kwargs):
    '''histogramMap(arr, **kwargs)
    Returns an array where the values are replaced with
    histogram values.
    '''
    arr=arrIn.copy();
    pdf,bins=P.np.histogram(arr, **kwargs);
    for b in xrange(len(bins)):
        if b == 0:
            arr[arr<bins[b]]=pdf[b];
        elif b==len(bins)-1:
            arr[arr>bins[b]]=pdf[b-1];
        else:
            arr[ (arr>bins[b])&(arr<bins[b+1]) ] = pdf[b];
    return arr

def sensitivity_plot(lvar, lnames):
    """fg=sensitivity_plot(lvar, lnames)
    Creates a plot for parameter correlation. The design of the plot is after the InSAR group at Oxford (Parsons)
    """
    #Now the hard part... Plotting 
    fg=P.figure()    
    #First we need to know how many variables (nvar)
    #nvel, nf, nalpha, A, B, E, and result(H)
    nvar=len(lvar)
    #now put all variables in a list
    #lvar=[nvel,nf,nalpha,nA,nB,nE,nH]
    #list of names
    #lnvar=['vel','f','slope','A','B','E','H']
    lnvar=lnames
    #now we create subplot (nvar-1 x nvar-1)    
#    for k in xrange(nvar-1):
#        for l in xrange(nvar-1-k):
#            ax = P.subplot(nvar-1, nvar-1, l*(nvar-1)+k+1, ) # aspect='equal',autoscale_on=False, xlim=[1,3], ylim=[1,3])
#            P.scatter(lvar[k], lvar[l+k+1], 5, c='k', marker='.');
#            P.axis('tight')
#            P.gca().xaxis.get_major_locator()._nbins=4 
#            P.gca().yaxis.get_major_locator()._nbins=4 
#            P.xlabel(lnvar[k]);
#            P.ylabel(lnvar[l+k+1]);
    for k in xrange(nvar-1):
        for l in xrange(k+1):
            plnum=k*(nvar-1)+l+1 #plotnumber
            if plnum == (nvar-1)**2:
                kk=nvar -2
            else:
                kk=plnum % (nvar-1) -1
            ll=N.int(N.ceil(plnum/float(nvar-1)))
            ax = P.subplot(nvar-1, nvar-1, plnum, ) # aspect='equal',autoscale_on=False, xlim=[1,3], ylim=[1,3])
            P.scatter(lvar[kk], lvar[ll], 5, c='k', marker='.');
            P.axis('tight')
            P.gca().xaxis.get_major_locator()._nbins=4 
            P.gca().yaxis.get_major_locator()._nbins=4 
            P.xlabel(lnvar[kk]);
            P.ylabel(lnvar[ll]);
    P.tight_layout(pad=0.005, w_pad=0.005, h_pad=0.005)    
    return fg
    
def manual_translation(master, slave):
    def onrelease(event):
        global coord
        try:
            x=np.round(event.xdata);
        except:
            return
        y=np.round(event.ydata);
        imshow_box(fig,master,x,y, s);
        coord=(x,y);
        
    def onkeypress(event):
        #print('you pressed', event.key, event.xdata, event.ydata)
        global coord
        x,y=coord
        if event.key == "up":
            y=y-1;
        elif event.key == "down":
            y=y+1;
        elif event.key =="left":
            x=x-1
        elif event.key == "right":
            x=x+1
        coord=(x,y);
        imshow_box(fig,master,x,y, s);
        
    def imshow_box(f,im, x,y,s):
        '''imshow_box(f,im, x,y,s)
        f: figure
        im: image
        x: center coordinate for box
        y: center coord
        s: box shape, (width, height)
        '''
        global coord
        P.figure(f.number)
        P.clf();
        P.imshow(im);
        P.axhline(y-s[1]/2.)
        P.axhline(y+s[1]/2.)
        P.axvline(x-s[0]/2.)
        P.axvline(x+s[0]/2.)
        xy=crop(m,s,y,x)
        coord=(0.5*(xy[2]+xy[3]), 0.5*(xy[0]+xy[1]))
        P.title(str('x: %d y: %d' % (x,y)));        
        P.figure(999);
        P.imshow(master[xy[0]:xy[1],xy[2]:xy[3]])
        P.title('Master');
        P.figure(998);
        df=(master[xy[0]:xy[1],xy[2]:xy[3]]-slave)
        P.imshow(np.abs(df))
        P.title(str('RMS: %0.6f' % np.sqrt((df**2.).mean()) ));        

    def crop(m,s,x,y):
      xy=[round(k) for k in [x-s[0]/2. , x+s[0]/2. ,   y-s[1]/2., y+s[1]/2.]]
      #print xy
      if np.any(xy<0):
        if xy[0]<0:
          xy[1]=xy[1]-xy[0];xy[0]=0;
        if xy[2]<0:
          xy[3]=xy[3]-xy[2];xy[2]=0;
      if xy[1]>m[0]:
          xy[0]=xy[0]-(xy[1]-m[0]);xy[1]=m[0];
      if xy[3]>m[1]:
          xy[2]=xy[2]-(xy[3]-m[1]);xy[3]=m[1];
      return xy
    s=slave.shape  
    m=master.shape                     
    fig=P.figure();
    imshow_box(fig,master,m[0]*0.5,m[1]*0.5,s);
    coord=(m[0]*0.5,m[1]*0.5)
    P.figure();
    P.imshow(slave);P.title('Slave');
    fig.canvas.mpl_connect('button_release_event', onrelease);
    fig.canvas.mpl_connect('key_press_event', onkeypress);
    return fig   
    
def manual_translation_scatter(master, sx,sy,sz, dotsize=1):
    def onrelease(event):
        if event.button !=3:
            return
        global coord
        try:
            x=np.round(event.xdata);
        except:
            return
        y=np.round(event.ydata);
        imshow_box(fig,master,x,y, s);
        coord=(x,y);
        
    def onkeypress(event):
        #print('you pressed', event.key, event.xdata, event.ydata)
        global coord
        x,y=coord
        if event.key == "up":
            y=y-1;
        elif event.key == "down":
            y=y+1;
        elif event.key =="left":
            x=x-1
        elif event.key == "right":
            x=x+1
        coord=(x,y);
        imshow_box(fig,master,x,y, s);
        
    def imshow_box(f,im, x,y,s):
        '''imshow_box(f,im, x,y,s)
        f: figure
        im: image
        x: center coordinate for box
        y: center coord
        s: box shape, (width, height)
        '''
        global coord
        P.figure(f.number)
        P.clf();
        P.imshow(im);
        P.axhline(y)
        P.axhline(y+s[1])
        P.axvline(x)
        P.axvline(x+s[0])
        P.scatter(sx+x,sy+y, dotsize, sz, edgecolor='none');
        coord=(x,y);
        P.title(str('x: %d y: %d' % (x,y)));  
        
    s=(sx.max()-sx.min() , sy.max()-sy.min() )
    m=master.shape                     
    fig=P.figure();
    imshow_box(fig,master,m[0]*0.5,m[1]*0.5,s);
    coord=(m[0]*0.5,m[1]*0.5)
    fig.canvas.mpl_connect('button_release_event', onrelease);
    fig.canvas.mpl_connect('key_press_event', onkeypress);
    return fig     

def z2rgb(z):
  z=abs(np.log10(z))*np.exp(1j*np.angle(z));
  r = abs(z);
  [d1,d2]=z.shape;
  a = np.sqrt(1/6)*np.real(z);
  b = np.sqrt(1/2)*np.imag(z);
  d = 1./(1+r**2);
  R = 1/2 + np.sqrt(2/3)*np.real(z)*d;
  G = 1/2 - d*(a-b);
  B = 1/2 - d*(a+b);
  d = 1/2 - r*d;
  d[r<1] = -d[r<1];
  C=np.zeros([d1,d2,3]);
  C[:,:,0] = R + d;
  C[:,:,1] = G + d;
  C[:,:,2] = B + d;
  f=P.figure();
  P.imshow(C);  
  return f

def z2rgba(z):
  z=abs(np.log10(z))*np.exp(1j*np.angle(z));
  r = abs(z);
  [d1,d2]=z.shape;
  a = np.sqrt(1/6)*np.real(z);
  b = np.sqrt(1/2)*np.imag(z);
  d = 1./(1+r**2);
  R = 1/2 + np.sqrt(2/3)*np.real(z)*d;
  G = 1/2 - d*(a-b);
  B = 1/2 - d*(a+b);
  d = 1/2 - r*d;
  d[r<1] = -d[r<1];
  C=np.zeros([d1,d2,3]);
  C[:,:,0] = R + d;
  C[:,:,1] = G + d;
  C[:,:,2] = B + d;
  f=P.figure();
  P.imshow(C);  
  return f

def distance_from_colorbar(im, c=P.cm.jet(np.arange(256))):
  """ This function calculates a distance value for all pixels of an image given a colorbar. 
      It also returns the best fitting colorbar class for each pixel.
  e.g.: 
    import cv2
    im=cv2.cvtColor(cv2.imread('REsults_zonaSur_cut.tiff'), cv2.COLOR_BGR2RGB);
    dist, classes=distance_from_colorbar(im);
  """
  import time
  N=c.shape[0];
  cmax=2**np.round(np.log2(im.max()))
  if c.max() != cmax:
    c256=c*cmax/c.max(); #colorbar in uint8 
  else:
    c256=c;
      
  dist=np.ones((im.shape[0], im.shape[1]))*np.inf; 
  distOld=dist.copy();
  classes=np.zeros((im.shape[0], im.shape[1]));
  ccc=0; #current class counter
  t0=0; #time.time(); #show 0.0 at the beginning of the loop. 
  for k in c256:
    dist   =np.dstack([dist, np.sqrt( (im[:,:,0]-k[0])**2. + (im[:,:,1]-k[1])**2. + (im[:,:,2]-k[2])**2. )]).min(2);
    classes[dist!=distOld]=ccc;
    ccc=ccc+1;distOld=dist;
    if basic.progresstime(t0):
      basic.progress(ccc,N);t0=time.time();
  return dist, classes;

def data_from_image(im, classes, mask, limits=[0.,1.]):
  """ This function extracts the data from a image, based on the classes and a mask. 
      Once the data is masked, a look-up-table is used to set values to the classes. 
  """
  import time;
  N=int (basic.nonan(classes).max()+1) ; # zero is a class... 
  classes[mask]=np.nan
  classLimits=np.linspace(np.min(limits), np.max(limits), N);
  
  cmax=2**np.round(np.log2(im.max()));
  imSingle=im[:,:,0]*(cmax**0)+im[:,:,1]*(cmax**1)+im[:,:,2]*(cmax**2.);
  data=np.zeros(imSingle.shape); 
  t0=0;
  for k in xrange(N-1):
    #for each class do a linear interpolation
    if np.any(classes==k):
      data[classes==k]=basic.rescale(imSingle[classes==k], classLimits[k:k+2], quiet=True);
    if basic.progresstime(t0):
      basic.progress(k,N); t0=time.time();
  data[mask]=np.nan;
  return data;

def class2data(classes, c=P.cm.jet(np.arange(256)), limits=[0., 1.]):
  """ Find the closest value in the colormap.
  """
  N=c.shape[0];
  data=classes/N*[np.max(limits)-np.min(limits)]+np.min(limits)
  return data;
 

#http://stackoverflow.com/questions/1679126/how-to-plot-an-image-with-non-linear-y-axis-with-matplotlib-using-imshow/6788842#6788842
def scalogram(data, vmin=None, vmax=None, linear=False):
    """ scalogram(data, vmin=None, vmax=None)
    Plots a scalogram for wavelet transforms generated by
    pywt.wavedec using imshow.
    """
    bottom = 0

    if not vmin:
    	vmin = min(map(lambda x: min(abs(x)), data))
    if not vmax:
    	vmax = max(map(lambda x: max(abs(x)), data))

    if linear:
    	scale=1./len(data);
    
    P.gca().set_autoscale_on(False)

    for row in range(0, len(data)):
        if not linear:
            scale = 2.0 ** (row - len(data))

        P.imshow(
            np.array([abs(data[row])]),
            interpolation = 'nearest',
            vmin = vmin,
            vmax = vmax,
            extent = [0, 1, bottom, bottom + scale])

        bottom += scale

def scalogram2(data, vmin=None, vmax=None, max_level=None, scale=None, percent=False, verbose=False):
    """ scalogram2(data, vmin=None, vmax=None)
    Plots a 2D scalogram for wavelet transforms generated by
    pywt.wavedec2 using imshow.
    """

    if percent==True:
      maxData=[]
      sumData=[]
      sumData.append(abs(data[0]).sum());
      #sumData=0;     
      maxData.append(abs(data[0]).max())
      for row in range(1,len(data)):
        sumData.append(abs(data[row][0]).sum()); sumData.append(abs(data[row][1]).sum()); sumData.append(abs(data[row][2]).sum());
        maxData.append(abs(data[row][0]).max()); maxData.append(abs(data[row][1]).max()); maxData.append(abs(data[row][2]).max());
      sumData=np.array(sumData)
      maxData=np.array(maxData)
      multiplier=1./maxData;
      if verbose:
        print('sumData');print(sumData);
        print('maxData');print(maxData);
        print('multiplier'); print(multiplier);
    else:
      multiplier=np.ones([1,len(data)*3+1]);
    if not max_level:
      max_level=len(data);
    if scale=='power' or scale=='logpower':
      ppower=(len(data)+1)**2*np.ones(data[0].shape);
    approx=abs(data[0])*multiplier[0];
    #P.matshow(approx);P.title('Preloop');
    for row in range(1,len(data)):
        #scale = 2.0 ** (row - len(data))
        #print row
        #print approx.shape
        #print data[row][0].shape
        if approx.shape[0]<> data[row][0].shape[0]:            
            approx=basic.resize(approx, data[row][0].shape);
            if scale=='power' or scale=='logpower':
              ppower=basic.resize(ppower, data[row][0].shape);  
            #print basic.resize
        arr=np.zeros([ data[row][0].shape[0]*2, data[row][0].shape[1]*2] )
        #print arr.shape
        #print approx.shape
        #P.matshow(approx);P.title(['Row', str(row)]);
        if verbose:
           print('0 Min: %E    Max: %E' % (abs(data[row][0]).min(), abs(data[row][0]).max()))
           print('1 Min: %E    Max: %E' % (abs(data[row][1]).min(), abs(data[row][1]).max()))
           print('2 Min: %E    Max: %E' % (abs(data[row][2]).min(), abs(data[row][2]).max()))
        
        arr[0:approx.shape[0], 0:approx.shape[1]]=approx;
        arr[0:approx.shape[0], approx.shape[1]: ]=abs(data[row][0])*multiplier[row*3-2];
        arr[approx.shape[0]: , 0:approx.shape[1]]=abs(data[row][1])*multiplier[row*3-1];
        arr[approx.shape[0]: , approx.shape[1]: ]=abs(data[row][2])*multiplier[row*3];
        approx=arr; #save for next loop.
        if scale=='power' or scale=='logpower':
          power=(len(data)+1-row)**2*np.ones([ data[row][0].shape[0]*2, data[row][0].shape[1]*2] )
          power[0:ppower.shape[0], 0:ppower.shape[1]]=ppower;
          ppower=power;
        if row==max_level:
            break


    if not vmin:
    	vmin = min(arr.ravel())
    if not vmax:
    	vmax = max(arr.ravel())        
    P.figure();   
    P.gca().set_autoscale_on(False)
    if scale=='log':
        P.imshow(
            10*np.log10(arr),
            interpolation = 'nearest',
            vmin = 10*np.log10(vmin),
            vmax = 10*np.log10(vmax),
            extent = [0, 1, 0, 1])      
        P.colorbar();
        P.title('Logscale')
    elif scale=='sqrt':
        P.imshow(
            np.sqrt(arr),
            interpolation = 'nearest',
            vmin = np.sqrt(vmin),
            vmax = np.sqrt(vmax),
            extent = [0, 1, 0, 1])      
        P.colorbar();
        P.title('SQRT')        
    elif scale=='power':
    	vmin = min((arr/power).ravel())
    	vmax = max((arr/power).ravel())
        P.imshow(
            arr/power,
            interpolation = 'nearest',
            vmin = vmin,
            vmax = vmax,
            extent = [0, 1, 0, 1])      
        P.colorbar();
        P.title('Power')
    elif scale=='logpower':
    	vmin = min((10*np.log10(arr/power)).ravel())
    	vmax = max((10*np.log10(arr/power)).ravel())
        P.imshow(
            10*np.log10(arr/power),
            interpolation = 'nearest',
            vmin = vmin,
            vmax = vmax,
            extent = [0, 1, 0, 1])      
        P.colorbar();
        P.title('LogPower')
    else:            
        P.imshow(
            arr,
            interpolation = 'nearest',
            vmin = vmin,
            vmax = vmax,
            extent = [0, 1, 0, 1])  
        P.colorbar();
        P.title('Linear scale') 
    if verbose:
      print('vmin: %E, vmax: %E ' %(vmin, vmax))
    #Draw Dividers
    for r in xrange(1,max_level):
        s = 2.0 ** (r - max_level); #s=scale, but scale is used above and below 
        lim=2.*s;        
        #print scale
        P.plot([s, s],[1-lim, 1], 'r', linewidth=4)
        P.plot([0, lim],[1-s, 1-s], 'r', linewidth=4)
    if scale=='power' or scale=='logpower':
        P.matshow(power);P.colorbar();P.title('Denominator');
    return arr

def mapshow(lon,lat, z):
  from mpl_toolkits.basemap import Basemap
  if lat.ndim==1:
    d0,d1=numpy.meshgrid(numpy.linspace(lat.min(),lat.max(), lon.shape[1]),
    numpy.linspace(lon.min(), lon.max(), lon.shape[0]))
    z = interpolate.griddata((lon.ravel(),lat.ravel()), z.ravel(), (d1, d0), method='linear')
  else:
    d0=lon;d1=lat;
  if lat[0,0] > 0: #northern hemisphere
    if d1[0,0]<d1[-1,0]:
      d1=numpy.flipud(d1)

  print ('Please wait... Generating map\n')
  m = Basemap(llcrnrlon=d0.min(), llcrnrlat=d1.min(), urcrnrlon=d0.max(), urcrnrlat=d1.max(),
    resolution='f', area_thresh=1., projection='cyl')
  m.imshow(z, interpolation='nearest', origin='upper')
  m.drawcoastlines(color='w',linewidth=0.8)
  m.drawmapboundary() # draw a line around the map region
  m.drawrivers()
  m.drawparallels(numpy.arange(int(d1.min()), int(d1.max()), 1),linewidth=0.2,labels=[1,0,0,0])
  m.drawmeridians(numpy.arange(int(d0.min()), int(d0.max()), 1),linewidth=0.2,labels=[0,0,0,1])    

