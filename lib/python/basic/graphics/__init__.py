import numpy as np
import pylab as P
import basic

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

def clickScat(array2d, array3d, xScat=None, xerror3d=None, yerror3d=None, array3d2=None, xerror3d2=None, yerror3d2=None, fn=None, xMap=None, yMap=None):
    """
    figureHandles=clickScat(array2d, array3d, xScat=None, xerror3d=None, yerror3d=None, array3d2=None, xerror3d2=None, yerror3d2=None, fn=None, xMap=None, yMap=None):
    xScat: x-axis variables for Scatter Plot. Has to be the same length as last dimension of array3d.shape[2]
    xerror3d: errorbars for x-axis. two sided. 
    fn:'annual'
    """
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
        
        if (yerror3d is None) and (xerror3d is None):
            P.scatter(xScat,array3d[x, y,:]);
        elif (xerror3d is None):
            P.errorbar(xScat,array3d[x, y,:], yerr=yerror3d[x, y,:], fmt='ro');
        elif (yerror3d is None):
            P.errorbar(xScat,array3d[x, y,:], xerr=xerror3d[x,y,:], fmt='ro');
        else:
            P.errorbar(xScat,array3d[x, y,:], xerr=xerror3d[x,y,:], yerr=yerror3d[x, y,:], fmt='ro');
        #Plot second scatter data.
        if array3d2 is not None:
            #P.scatter(xScat, array3d2[x, y,:], marker='*');
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
                import scipy
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
                import scipy
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
                import scipy
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
    
def linkedImShow(im1, im2):    
    P.figure();
    ax1 = P.subplot(111)
    P.figure();
    ax2 = P.subplot(111, sharex=ax1, sharey=ax1)
    
    #ax1.set_adjustable("box-forced")
    #ax2.set_adjustable("box-forced")
    
    #arr1 = np.arange(100).reshape((10, 10))
    ax1.imshow(im1)
    
    #arr2 = np.arange(100, 0, -1).reshape((10, 10))
    ax2.imshow(im2)
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

def frankotchellappaiter(dzdx,dzdy,weight=None, threshold=0.1, maxiter=10):
    '''frankotchellappaiter(dzdx,dzdy):
    '''
    import scipy
    scipy.pkgload('ndimage');
    
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
    
